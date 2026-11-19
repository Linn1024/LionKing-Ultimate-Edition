"""Attribute apparent unmapped sprite poses to their live HUD/caption owners."""
import ctypes as C
import json
import os
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-effect-coverage';source=base/'report.json';prior=bound(source)
    assert prior['result']=='PASS' and len(prior['unknown_pairs'])==3
    out=base/'dynamic-packets2';out.mkdir();commands={};checks={}
    template=prior['commands']['aot'].copy();i=template.index('--hash-at');del template[i:i+2]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(label,frames,load=None,tape=None,debugger=None,save=False):
        folder=out/label;folder.mkdir();cmd=template.copy()
        for flag,value in [('--frames',frames),('--dump-window',folder/'window.png'),
                            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        if load:cmd+=['--load',str(load)]
        if tape:cmd[cmd.index('--input-polled')+1]=str(tape)
        if save:cmd+=['--save-at',str(frames),str(folder/'saved.state')]
        if debugger:cmd=['C:/mingw32/bin/gdb.exe','--batch','-x',str(debugger),'--args',*cmd]
        commands[label]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_SPRITE_OBJECTS=str(folder/'objects.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[label+'_exit']=rc==0;print(label,rc,flush=True);return folder
    script=out/'owners.gdb'
    lines=['set pagination off','set confirm off','set $saved0=0','set $saved1=0','set $saved2=0','break RecordPiece','disable 1','commands','silent',
           'set $guest_d=*(unsigned short*)((char*)&g_cpu+8)',
           'set $draw=*(unsigned short*)((char*)&g_ram+$guest_d+0x7c)',
           'set $pose=(*(unsigned int*)((char*)&g_ram+$guest_d+0x85))&0xffffff']
    captures=[]
    for n,(name,draw,pose,field) in enumerate([('roar',0xdc24,0xc00006,1038),('health',0xdc35,0xc0d5de,1038),('caption',0xdc68,0x7e17dd,1040)]):
        path=out/(name+'-wram.bin');captures.append((name,draw,pose,path))
        lines += [f'if $saved{n}==0 && $draw=={draw} && $pose=={pose} && *(unsigned int*)&snes_frame_counter=={field}',
                  f'printf "OWNER name={name} draw=%x pose=%x d=%x\\n",$draw,$pose,$guest_d',
                  f'dump binary memory {path.as_posix()} &g_ram ((char*)&g_ram+0x20000)',f'set $saved{n}=1','end']
    lines+=['continue','end','break __wrap_RtlRunFrame','commands','silent','if *(unsigned int*)&snes_frame_counter>=1038 && *(unsigned int*)&snes_frame_counter<=1040','enable 1','else','disable 1','end','continue','end','run'];script.write_text('\n'.join(lines)+'\n')
    control=run('control',1042)
    debug=run('debugger',1042,debugger=script)
    def hashes(folder):return re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',(folder/'run.log').read_text(),re.M)
    checks['debugger_guest_neutral']=bool(hashes(control)) and hashes(control)==hashes(debug)
    for name in ('window.png','scene.json','audio.wav','objects.csv','tree.jsonl'):
        checks['debugger_'+name+'_neutral']=digest(control/name)==digest(debug/name)
    wrapper=out/'roles.c';wrapper.write_text('#include "tlk_hud_role.h"\n#include "tlk_title_role.h"\n'
        'int hud(const uint8_t*r,unsigned n,const uint8_t*s,unsigned z,unsigned d,int f){return TlkHudMeterRole(r,n,s,z,d,f!=0);}\n'
        'int caption(const uint8_t*r,unsigned n,const uint8_t*s,unsigned z,unsigned d,unsigned p,int f){return TlkPrideTitleDrawRole(r,n,s,z,d,p,f!=0);}\n')
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(ROOT/'engine/runner'),str(wrapper),'-o',str(out/'roles.dll')]
    subprocess.run(command,check=True);commands['compile_roles']=command
    lib=C.CDLL(str(out/'roles.dll'));lib.hud.argtypes=[C.c_void_p,C.c_uint,C.c_void_p,C.c_uint,C.c_uint,C.c_int]
    lib.caption.argtypes=lib.hud.argtypes[:-1]+[C.c_uint,C.c_int]
    rom=(ROOT/'Lion King, The (USA).sfc').read_bytes();rom_buffer=C.create_string_buffer(rom);owners=[]
    for name,draw,pose,path in captures:
        checks[name+'_captured']=path.exists()
        if not path.exists():continue
        ram=path.read_bytes();buffer=C.create_string_buffer(ram)
        role=lib.caption(buffer,len(ram),rom_buffer,len(rom),draw,pose,0) if name=='caption' else lib.hud(buffer,len(ram),rom_buffer,len(rom),draw,1)
        checks[name+'_existing_semantic_guard_matches']=role==({'roar':0,'health':1,'caption':1}[name])
        actor=int.from_bytes(ram[draw+4:draw+6],'little')-8
        owners.append(dict(name=name,draw=draw,pose=pose,actor=actor,
                           descriptor=int.from_bytes(ram[actor+4:actor+7],'little'),
                           action=int.from_bytes(ram[actor+0x30:actor+0x33],'little'),role=role))
    paths=[Path(__file__),source,script,wrapper,ROOT/'engine/runner/tlk_hud_role.h',ROOT/'engine/runner/tlk_title_role.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,owners=owners,
                reads_only_guest_state=True,runtime_or_renderer_changed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),owners,flush=True)


if __name__=='__main__':main()
