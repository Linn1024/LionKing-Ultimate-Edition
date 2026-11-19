"""Test native scheduling with an experimental output-only bounce replacement."""
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
    public=ROOT/'build/pride-lizard-launch-work/player';base=public/'bounce-output-prototype2'
    bp=base/'build-report.json';build=bound(bp);assert digest(base/'player.exe')==build['binary_sha256']
    rp=public/'launch-audio-baselines/report.json';assert bound(rp)['result']=='PASS'
    out=base/'verification';out.mkdir();checks={};commands={};runs={}
    config=public/'launch-audio/host.ini';tape=ROOT/'engine/tapes/allbugsF.read.tape'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    production=public/'launch-audio/native-aot'
    native_rows=re.findall(pattern,(production/'run.log').read_text())
    for mode in ('aot','lle'):
        for name in ('native','bounce'):
            label=name+'-'+mode;folder=out/label;folder.mkdir()
            env=dict(clean,TLK_BOUNCE_NPC_TRACE=str(folder/'npc.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
            command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                '--md-rom',ROOT/'Lion King, The (World).md','--config',config,
                '--resource-profile',public/f'launch-audio/{name}.ini','--input-polled',tape,
                '--frames',4500,'--no-pace','--no-audio','--no-record',
                '--hash-at',','.join(map(str,range(1,4501))),'--wav',folder/'audio.wav','--wav-seconds',100,
                '--dump-window',folder/'window.png']))
            if mode=='lle':command+=['--lle']
            commands[label]=command
            with (folder/'run.log').open('wb') as log:
                subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=400)
            rows=re.findall(pattern,(folder/'run.log').read_text())
            checks[label+'/all_fields']=len(rows)==4500
            checks[label+'/every_native_guest_field']=rows==native_rows
            checks[label+'/native_actual_client']=pixels(folder/'window.png')==pixels(production/'window.png')
            with (folder/'driver.csv').open() as stream:driver=list(csv.DictReader(stream))
            count=sum(r['selector']=='2' and r['value']=='123' for r in driver)
            checks[label+'/source_command_count']=count==(6 if name=='bounce' else 0)
            npc=(folder/'npc.csv').read_bytes() if (folder/'npc.csv').exists() else None
            runs[label]=dict(rows=rows,pcm=wav_data(folder/'audio.wav'),npc=npc)
            print(label,'native guest exact',rows==native_rows,'FM123',count,flush=True)
    for name in ('native','bounce'):
        a,b=runs[name+'-aot'],runs[name+'-lle']
        checks[name+'/entire_mode_pcm']=a['pcm']==b['pcm']
    checks['native_whole_production_pcm']=runs['native-aot']['pcm']==wav_data(production/'audio.wav')
    checks['replacement_audible']=runs['bounce-aot']['pcm']!=runs['native-aot']['pcm']
    checks['lle_complete_npc_and_gate_trace_preserved']=bool(runs['native-lle']['npc']) and runs['native-lle']['npc']==runs['bounce-lle']['npc']
    paths=[Path(__file__),bp,rp,tape,public/'launch-audio/native-aot/run.log',production/'audio.wav',production/'window.png']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        sample_ownership_scope_proven=False,prototype_only=True,production_changed=False,
        full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'prototype checks',flush=True);assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
