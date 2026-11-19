"""Exercise original Options/return and maintained Windows title lifecycle."""
import ctypes as C
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,MdLab,png
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-title-ready18';source=base/'verification/report.json';old=bound(source)
    original=ROOT/'build/pride-title-readiness-original';bound(original/'report.json')
    histories=ROOT/'build/pride-title-readiness-probe3/contexts';bound(histories/'report.json')
    context=bound(base/'contexts/report.json')
    out=base/'options';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    plans={
        'options':(550,{515:'down',516:'start'}),
        'return':(620,{515:'down',516:'start',600:'start'}),
        'newgame':(1251,{515:'down',516:'start',600:'start',650:'up',651:'start'}),
        'repress':(933,{331:'start',333:'start'})}
    buttons={'down':(32,0x400),'up':(16,0x800),'start':(8,0x1000)}
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    states={}
    try:
        for label,(end,events) in plans.items():
            state=histories/'go-start140/original-before-input.state' if label=='repress' else original/'game-over-timeout/before-input.state'
            states[label]=state;raw=state.read_bytes();blob=C.create_string_buffer(raw);assert game.core.retro_unserialize(blob,len(raw))
            first=300 if label=='repress' else 484;rows=[]
            for age in range(first,end+1):
                game.step(buttons[events[age]][0] if age in events else 0);game.samples.clear()
                if age in events or age%10==0:
                    word=lambda p:game.work_ram[p]|game.work_ram[p+1]<<8
                    rows.append(dict(age=age,level=word(0xccce),health=word(0xccf6),lives=word(0xccee)))
            png(out/f'original-{label}.png',*game.image);observations[label]=rows
    finally:game.close()
    def run(width,label,end,events,lle=False,load=None,save=False):
        folder=out/f'{width}-{label}'
        folder.mkdir()
        template=context['commands']['go-start140-neutral-normal'] if 'repress' in label else old['commands'][f'{width}-neutral']
        cmd=template.copy()
        # The prior-Start fixture shares the same viewport-independent native state.
        if 'repress' in label:cmd[cmd.index('--resource-profile')+1]=old['commands'][f'{width}-neutral'][old['commands'][f'{width}-neutral'].index('--resource-profile')+1]
        if '--save-at' in cmd:
            i=cmd.index('--save-at');del cmd[i:i+3]
        if '--lle' in cmd:cmd.remove('--lle')
        if lle:cmd.append('--lle')
        data=bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes());data.extend(bytes(max(0,(4444+end+1)*2-len(data))))
        for age,key in events.items():struct.pack_into('<H',data,(4444+age-1)*2,buttons[key][1])
        tape=folder/'input.tape';tape.write_bytes(data)
        for flag,value in [('--input',tape),('--frames',4444+end),('--config',out/'host.ini'),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if load:cmd[cmd.index('--load')+1]=str(load)
        if save:cmd+=['--save-at',str(4444+end),str(folder/'saved.state')]
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1'),stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        checks[folder.name+'_exit']=r.returncode==0;commands[folder.name]=cmd;print(folder.name,r.returncode,flush=True)
        return folder
    def same(label,a,b,skip=0):
        checks[label+'_client']=(a/'window.png').exists() and pixels(a/'window.png')==pixels(b/'window.png')
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[label+'_pcm']=(a/'audio.wav').exists() and pcm(a/'audio.wav')==pcm(b/'audio.wav')[skip:]
    for width in (256,320):
        live={}
        for label,(end,events) in plans.items():
            live[label]=run(width,label,end,events,save=label=='options')
            alternate=run(width,label+'-lle',end,events,lle=True)
            same(f'{width}_{label}_lle',alternate,live[label])
            scene=json.loads((live[label]/'scene.json').read_text())
            checks[f'{width}_{label}_stage']=scene['stage_detected']==(label in ('newgame','repress'))
        for label in ('return','newgame'):
            end,events=plans[label];cold=run(width,label+'-cold',end,events,load=live['options']/'saved.state')
            same(f'{width}_{label}_cold',cold,live[label],len(pcm(live['options']/'audio.wav')))
        raw=(live['options']/'saved.state').read_bytes();at=96+struct.unpack_from('<I',raw,20)[0]
        checks[f'{width}_options_retired']=struct.unpack_from('<I',raw,at+100)[0]==0 and raw[at+172:at+180]==bytes(8)
    paths=[Path(__file__),source,base/'contexts/report.json',original/'report.json',histories/'report.json',*states.values()]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,original_observations=observations,
                original_guest_or_rom_edits=False,full_options_or_transition_parity_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
