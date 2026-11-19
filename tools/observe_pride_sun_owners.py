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
    assert prior['result']=='PASS'
    out=base/'sun-owners';out.mkdir();commands={};checks={}
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
    for n,(name,draw,pose,field) in enumerate([('sun0',0xdcf0,0xc6f764,2506),('sun1',0xdcf0,0xc6f79b,2508),('sun2',0xdcf0,0xc6f7ce,2513),('sun3',0xdcf0,0xc6f801,2518)]):
        path=out/(name+'-wram.bin');captures.append((name,draw,pose,path))
        lines += [f'if $saved{n}==0 && $draw=={draw} && $pose=={pose} && *(unsigned int*)&snes_frame_counter=={field}',
                  f'printf "OWNER name={name} draw=%x pose=%x d=%x\\n",$draw,$pose,$guest_d',
                  f'dump binary memory {path.as_posix()} &g_ram ((char*)&g_ram+0x20000)',f'set $saved{n}=1','end']
    lines+=['continue','end','break __wrap_RtlRunFrame','commands','silent','if *(unsigned int*)&snes_frame_counter>=2506 && *(unsigned int*)&snes_frame_counter<=2518','enable 1','else','disable 1','end','continue','end','run'];script.write_text('\n'.join(lines)+'\n')
    control=run('control',2520)
    debug=run('debugger',2520,debugger=script)
    def hashes(folder):return re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',(folder/'run.log').read_text(),re.M)
    checks['debugger_guest_neutral']=bool(hashes(control)) and hashes(control)==hashes(debug)
    for name in ('window.png','scene.json','audio.wav','objects.csv','tree.jsonl'):
        checks['debugger_'+name+'_neutral']=digest(control/name)==digest(debug/name)
    owners=[]
    for name,draw,pose,path in captures:
        checks[name+'_captured']=path.exists()
        if not path.exists():continue
        ram=path.read_bytes();actor=int.from_bytes(ram[draw+4:draw+6],'little')-8
        owners.append(dict(name=name,draw=draw,pose=pose,actor=actor,
                           descriptor=int.from_bytes(ram[actor+4:actor+7],'little'),
                           action=int.from_bytes(ram[actor+0x30:actor+0x33],'little'),
                           animation=int.from_bytes(ram[actor+0xe:actor+0x11],'little'),
                           lives=int.from_bytes(ram[0x2006:0x2008],'little')))
    paths=[Path(__file__),source,script,ROOT/'engine/runner/tlk_hud_role.h',ROOT/'engine/runner/tlk_title_role.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,owners=owners,
                reads_only_guest_state=True,runtime_or_renderer_changed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),owners,flush=True)


if __name__=='__main__':main()
