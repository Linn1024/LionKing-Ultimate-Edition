"""Selected RNG source: AOT/LLE, raw saves, replay and mismatch rejection."""
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-rng-player';bp=base/'build-report.json';build=bound(bp);out=base/'source';out.mkdir();checks={};commands={}
    md=out/'md.ini';md.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.random_entry = md\n')
    native=out/'snes.ini';native.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.random_entry = snes\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for mode in ('aot','lle'):
        root=out/mode;root.mkdir();state=root/'ordinary.state'
        for name in ('cold','resumed','mismatch'):
            folder=root/name;folder.mkdir();cfg=folder/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
            cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',native if name=='mismatch' else md,'--config',cfg,'--input',tape,'--frames',3000,
                 '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,3001)))]
            if mode=='lle':cmd+=['--lle']
            if name=='cold':cmd+=['--save-at',1600,state]
            else:cmd+=['--load',state]
            if name!='mismatch':cmd+=['--wav',folder/'audio.wav','--wav-seconds',100,'--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
            commands[mode+'/'+name]=list(map(str,cmd));before=digest(state) if state.exists() else None
            with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[mode+'/'+name],cwd=ROOT,env=dict(env,TLK_RNG_ENTRY_TRACE=str(folder/'entry.csv')),stdout=log,stderr=subprocess.STDOUT,timeout=240)
            if name=='mismatch':
                checks[mode+'/source_mismatch_rejected']=r.returncode==8 and 'State scene-random source differs' in (folder/'run.log').read_text()
                checks[mode+'/input_preserved']=digest(state)==before;continue
            assert not r.returncode,(mode,name,r.returncode)
        data=state.read_bytes();checks[mode+'/source_flag_set']=data[:8]==b'TLKSTAT1' and int.from_bytes(data[32:36],'little')&0x40000000!=0
        a,b=root/'cold',root/'resumed';rows=lambda p:re.findall(pattern,(p/'run.log').read_text());actual=rows(b)
        checks[mode+'/every_resumed_field']=actual==[r for r in rows(a) if int(r[0])>1600] and len(actual)==1400
        audio=wav_data(b/'audio.wav');checks[mode+'/entire_resumed_pcm']=bool(audio) and audio==wav_data(a/'audio.wav')[-len(audio):]
        for what in ('guest','window'):checks[mode+'/'+what]=pixels(a/(what+'.png'))==pixels(b/(what+'.png'))
        checks[mode+'/normal_seed_applied']='aa0b4c' in (a/'entry.csv').read_text()
        checks[mode+'/load_does_not_reseed']=not (b/'entry.csv').exists()
        print(mode,[k for k,v in checks.items() if not v],flush=True)
    a,b=out/'aot/cold',out/'lle/cold';rows=lambda p:re.findall(pattern,(p/'run.log').read_text())
    checks['every_aot_lle_field']=len(rows(a))==3000 and rows(a)==rows(b)
    checks['aot_lle_pcm']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
    for what in ('guest','window'):checks['aot_lle_'+what]=pixels(a/(what+'.png'))==pixels(b/(what+'.png'))
    paths=[Path(__file__),bp,tape,ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,native_fields_compared=5800,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
