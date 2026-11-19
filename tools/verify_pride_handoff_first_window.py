"""Capture the very first loaded Windows field at the former actor handoff failure."""
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_handoff_state import BASE
from probe_pride_preparation_state import frame_records
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def main():
    seed=BASE/'windows/md-polled-320-native-301-aot-lle';r=json.loads((seed/'report.json').read_text())
    assert r['result']=='PASS'
    for name,sha in r['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(seed/'revival.private-state')==r['state_sha256']
    reference=ROOT/'build/pride-actor-handoff/windows/md-polled-320-native-aot-owned-2331-edges'
    prior=json.loads((reference/'report.json').read_text())
    for name,sha in prior['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in prior['artifacts_sha256'].items():assert digest(reference/name)==sha,name
    results={}
    for mode in ('aot','lle'):
        folder=BASE/'first-window'/mode;folder.mkdir(parents=True,exist_ok=True)
        command=[c for c in r['commands']['resumed'] if c!='--lle']
        command[command.index('--frames')+1]='2331'
        for flag,file in (('--dump-window','window.png'),('--wav','audio.wav')):
            command[command.index(flag)+1]=str(folder/file)
        if mode=='lle':command+=['--lle']
        env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        assert run.returncode==0 and hashes(folder/'run.log')==prior['guest'],mode
        assert pixels(folder/'window.png')==pixels(reference/'window.png'),mode
        actual,expected=wav_data(folder/'audio.wav'),wav_data(reference/'audio.wav')
        assert len(actual)>0 and expected[-len(actual):]==actual,mode
        assert frame_records(folder/'render-owned.rgb',320)=={
            age:data for age,data in frame_records(reference/'render-owned.rgb',320).items() if age==302},mode
        results[mode]=dict(exit_code=run.returncode,guest=hashes(folder/'run.log'),client_pixels=640*448,
            pcm_bytes=len(actual),artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        print(mode,'first loaded client/scene/guest/PCM exact',flush=True)
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),seed/'report.json',seed/'revival.private-state',reference/'report.json',BASE/'build-report.json')}
    (BASE/'first-window.json').write_text(json.dumps(dict(result='PASS',cases=results,source_sha256=sources,
        full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
