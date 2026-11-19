"""Resume a genuine pre-Pride menu save through both later health deaths."""
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
    base=ROOT/'build/pride-launch4';bp=base/'build-report.json';build=bound(bp)
    out=base/'menu-save';out.mkdir();checks={};commands={};total=0
    profile=out/'resources.ini';profile.write_bytes((ROOT/'profiles/pride-development-preview.ini').read_bytes())
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for mode in ('aot','lle'):
        root=out/mode;root.mkdir();state=root/'menu.state'
        for name in ('cold','resumed'):
            folder=root/name;folder.mkdir();cfg=folder/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
            cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--config',cfg,'--resource-profile',profile,'--input',tape,'--frames',3000,'--no-audio','--no-pace','--no-record',
                 '--hash-at',','.join(map(str,range(1,3001))),'--wav',folder/'audio.wav','--wav-seconds',100,
                 '--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
            cmd+=['--save-at',600,state] if name=='cold' else ['--load',state]
            if mode=='lle':cmd+=['--lle']
            commands[mode+'/'+name]=list(map(str,cmd))
            with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[mode+'/'+name],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=240)
            checks[mode+'/'+name+'/exit']=not r.returncode
            assert not r.returncode,(mode,name,r.returncode)
        record=state.read_bytes();flags=int.from_bytes(record[32:36],'little')
        checks[mode+'/native_nonpride_record']=record[:8]==b'TLKSTAT1' and int.from_bytes(record[12:16],'little')==600 and flags&0x20000000!=0 and flags&0x80000000==0
        a,b=root/'cold',root/'resumed';rows=lambda p:re.findall(pattern,(p/'run.log').read_text());actual=rows(b);total+=len(actual)
        checks[mode+'/every_resumed_field']=len(actual)==2400 and actual==[r for r in rows(a) if int(r[0])>600]
        audio=wav_data(b/'audio.wav');checks[mode+'/entire_resumed_pcm']=bool(audio) and audio==wav_data(a/'audio.wav')[-len(audio):]
        for what in ('guest','window'):checks[mode+'/'+what]=pixels(a/(what+'.png'))==pixels(b/(what+'.png'))
        # The former player's cold route is already bound by its regression
        # report; retain every field, audio and picture through later revivals.
        reference=ROOT/'build/pride-launch3/regression/md-death'
        checks[mode+'/previous_cold_fields']=rows(a)==rows(reference)
        checks[mode+'/previous_cold_pcm']=wav_data(a/'audio.wav')==wav_data(reference/'audio.wav')
        print(mode,[k for k,v in checks.items() if not v],flush=True)
    cfg=out/'old.ini';cfg.write_text('opengl = 0\nscale = 2\n');oldstate=out/'old-menu.state'
    cmd=[ROOT/'build/pride-launch3/player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
         '--config',cfg,'--resource-profile',profile,'--input',tape,'--frames',601,'--no-audio','--no-pace','--no-record','--save-at',600,oldstate]
    commands['before']=list(map(str,cmd))
    with (out/'before.log').open('wb') as log:r=subprocess.run(commands['before'],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=120)
    checks['previous_failure_reproduced']=r.returncode==8 and not oldstate.exists() and 'cannot save state' in (out/'before.log').read_text()
    paths=[Path(__file__),bp,ROOT/'build/pride-launch3/build-report.json',ROOT/'build/pride-launch3/regression/report.json',ROOT/'profiles/pride-development-preview.ini',tape,ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,native_fields_compared=total,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
