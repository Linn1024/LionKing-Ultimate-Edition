"""Verify driver validation after loading existing tagged pre-key-on/boss saves."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    public=ROOT/'build/pride-lizard-launch-work/player';base=public/'bounce-driver-lifecycle-prototype'
    bp=base/'build-report.json';bound(bp)
    old=public/'bounce-semantic-save-prototype';sp=old/'saves/report.json';assert bound(sp)['result']=='PASS'
    out=base/'save-compatibility';out.mkdir();checks={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    cases=(('bounce-aot-1399','bounce',1399,1500),('bounce-lle-3982','bounce',3982,4100),('native-aot-1400','native',1400,1500))
    for label,profile,point,end in cases:
        state=old/'saves'/(label+'.state');suffix=old/'saves'/(label+'.polled.tape')
        expected=re.findall(pattern,(public/f'bounce-semantic-prototype4/verification/{profile}-aot/run.log').read_text())[point:end]
        for mode in ('aot','lle'):
            runs={}
            for variant,exe in (('previous',old/'player.exe'),('driver',base/'player.exe')):
                key=label+'-'+mode+'-'+variant;folder=out/key;folder.mkdir()
                command=list(map(str,[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                    '--config',public/'launch-audio/host.ini','--resource-profile',public/f'launch-audio/{profile}.ini',
                    '--input-polled',suffix,'--load',state,'--frames',end,'--no-pace','--no-audio','--no-record',
                    '--hash-at',','.join(map(str,range(point+1,end+1))),'--wav',folder/'audio.wav','--wav-seconds',100,
                    '--dump-window',folder/'window.png']))
                if mode=='lle':command+=['--lle']
                commands[key]=command
                env=dict(clean,TLK_SEMANTIC_OWNER_TRACE=str(folder/'ownership.csv'))
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
                rows=re.findall(pattern,(folder/'run.log').read_text())
                checks[key+'/every_native_guest_field']=rows==expected
                runs[variant]=(wav_data(folder/'audio.wav'),pixels(folder/'window.png'))
            key=label+'-'+mode
            checks[key+'/whole_continuation_pcm']=runs['driver'][0]==runs['previous'][0]
            checks[key+'/actual_client']=runs['driver'][1]==runs['previous'][1]
            print(key,'failed',[k for k,v in checks.items() if not v],flush=True)
    sources=[Path(__file__),bp,sp]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        scope='known-driver tagged loads; six combinations, native/MD, pre-key-on and boss',
        full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'driver save compatibility checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
