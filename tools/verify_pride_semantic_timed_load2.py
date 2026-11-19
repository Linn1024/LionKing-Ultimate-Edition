"""Rewind a live process across native voice key-on and replay its audio exactly."""
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
    public=ROOT/'build/pride-lizard-launch-work/player';base=public/'bounce-semantic-save-prototype'
    bp=base/'build-report.json';bound(bp)
    sp=base/'saves/report.json';assert bound(sp)['result']=='PASS'
    out=base/'timed-load2';out.mkdir();checks={};commands={}
    zero=out/'zero.tape';zero.write_bytes(bytes(1000))
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    states={'native':base/'saves/native-aot-1400.state','bounce':base/'saves/bounce-aot-1399.state'}
    for profile,state in states.items():
        for mode in ('aot','lle'):
            results={}
            for timed in (False,True):
                label=profile+'-'+mode+('-timed' if timed else '-control');folder=out/label;folder.mkdir()
                command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                    '--md-rom',ROOT/'Lion King, The (World).md','--config',public/'launch-audio/host.ini',
                    '--resource-profile',public/f'launch-audio/{profile}.ini','--load',state,
                    '--input-raw',zero,'--frames',1600,'--no-audio','--no-record',
                    '--hash-at',','.join(map(str,range(1399,1601))),
                    '--wav',folder/'audio.wav','--wav-seconds',100,'--dump-window',folder/'window.png']))
                if mode=='lle':command+=['--lle']
                if timed:command+=['--load-at','1450',str(state)]
                commands[label]=command
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(command,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
                log=(folder/'run.log').read_text()
                results[timed]=(re.findall(pattern,log),wav_data(folder/'audio.wav'),pixels(folder/'window.png'),log)
            a,b=results[False],results[True];key=profile+'-'+mode
            expected_fields=200 if profile=='native' else 201
            checks[key+'/control_fields']=len(a[0])==expected_fields
            checks[key+'/actual_live_rewind']=b[3].count('loaded_state=')==2 and ('-> 1400' if profile=='native' else '-> 1399') in b[3]
            checks[key+'/all_replayed_guest_fields']=b[0][-len(a[0]):]==a[0]
            checks[key+'/whole_replayed_pcm']=b[1][-len(a[1]):]==a[1] and len(b[1])>len(a[1])
            checks[key+'/actual_client']=b[2]==a[2]
            print(key,'failed',[k for k,v in checks.items() if not v],flush=True)
    sources=[Path(__file__),bp,sp,*states.values()]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        scope='neutral input at native1400 and MD1399; actual in-process rewind at1450',
        prototype_only=True,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'timed-load checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
