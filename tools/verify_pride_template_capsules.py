"""Observe all seven retained capsules while the original fallback decoder runs."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from capture_pride_ledge_physics import PATTERN
from pride_scene_template_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    probe=ROOT/'build/pride-bounce-owner-work/player/fallback-probe2';bp=probe/'build-report.json'
    assert digest(probe/'player.exe')==bound(bp)['binary_sha256']
    reference_path=ROOT/'build/pride-scene-template-work/player/fallback/report.json';reference=bound(reference_path)
    assert reference['result']=='PASS'
    ref=reference_path.parent/'candidate-md-lle'
    hashes=re.findall(PATTERN,(ref/'run.log').read_text());whole=wav_data(ref/'audio.wav')
    out=probe/'preserve';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=reference_path.parent/'md.ini';tape=ROOT/'build/pride-health-death-native/neutral-tail.polled.tape'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    checks={};commands={};journals={}
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir();env=dict(clean,TLK_TEMPLATE_PRESERVE=str(folder/'templates.csv'))
        command=list(map(str,[probe/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--config',config,'--resource-profile',profile,'--input-polled',tape,'--frames',5000,
            '--hash-at',','.join(map(str,range(1,5001))),'--no-pace','--no-audio','--no-record',
            '--wav',folder/'audio.wav','--wav-seconds',100,'--dump-window',folder/'window.png']))
        if mode=='lle':command+=['--lle']
        commands[mode]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        rows=list(csv.DictReader((folder/'templates.csv').open()));journals[mode]=rows
        checks[mode+'/all_5000_guest_fields']=re.findall(PATTERN,(folder/'run.log').read_text())==hashes
        checks[mode+'/whole_native_pcm']=wav_data(folder/'audio.wav')==whole
        checks[mode+'/whole_actual_client']=pixels(folder/'window.png')==pixels(ref/'window.png')
        checks[mode+'/all_7_capsules_and_payloads_unchanged']=len(rows)==14 and all(r['unchanged']=='1' for r in rows)
        checks[mode+'/faulting_recipe_executes_natively']=bool(rows) and rows[0]['source']=='ee6e03' and rows[0]['field']=='4819'
        checks[mode+'/all_original_recipe_bodies_complete']=[r['event'] for r in rows]==['entry','exit']*7
        print(mode,'capsule observer complete',len(rows),'records',flush=True)
    checks['both_mode_journals_exact']=journals['aot']==journals['lle']
    paths=[Path(__file__),bp,reference_path,profile,tape,ROOT/'engine/runner/pride/pride_scene_template.h']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        all_capsule_storage_and_payloads_unchanged_within_each_process=True,
        full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'capsule checks; failures',[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
