"""Audit same-process checkpoint rewind after caches have already been consumed.

Report any remaining host presentation/audio differences explicitly. A passing
new-process continuation alone does not establish this lifecycle behavior.
"""
import json
import os
from pathlib import Path
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_preparation_state import rows
from verify_windows import hashes,pixels


def pcm(path):
    with wave.open(str(path),'rb') as wav:return wav.readframes(wav.getnframes())


def main():
    base=ROOT/'build/pride-preparation-state';out=base/'rewind';out.mkdir(exist_ok=True)
    binary=base/'preparation-state-sdl.exe';identity=digest(binary);results={}
    for width,graphics,mode in ((256,'native','lle'),(320,'all','aot')):
        case=f'{width}-{graphics}-{mode}';folder=out/case;folder.mkdir(exist_ok=True)
        # Baselines were saved in opposite-mode pairs; this run itself keeps
        # its CPU mode while rewinding the live process.
        load='aot' if mode=='lle' else 'lle'
        reference=base/'windows'/f'{width}-{graphics}-4668-{mode}-{load}'/'baseline'
        profile=reference.parent/'resources.ini';state=folder/'checkpoint.private-state'
        env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--config',base/'windows/host.ini','--resource-profile',profile,'--frames','5400',
                 '--no-pace','--no-audio','--no-record','--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
                 '--save-at','4668',state,'--load-at','4704',state,'--dump-window',folder/'window.png',
                 '--wav',folder/'audio.wav','--wav-seconds','100']
        if mode=='lle':command.append('--lle')
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        report=dict(exit_code=result.returncode)
        if result.returncode==0:
            def remaining(path):
                records=rows(path);starts=[n for n,r in enumerate(records) if int(r['field'])==4669]
                assert starts
                return records[starts[-1]:]
            expected=pcm(reference/'audio.wav');actual=pcm(folder/'audio.wav')
            expected_tail=expected[(4668*48000*357366//21477272)*4:]
            report.update(endpoint_guest_exact=hashes(folder/'run.log')==hashes(reference/'run.log'),
                final_client_exact=pixels(folder/'window.png')==pixels(reference/'window.png'),
                remaining_scene_fields_exact=all(remaining(folder/name)==remaining(reference/name) for name in
                    ('owner-fields.csv','restore-fields.csv','render-fields.csv')),
                final_pcm_tail_exact=actual[-len(expected_tail):]==expected_tail,
                pcm_bytes=len(actual))
        report['artifacts_sha256']={p.name:digest(p) for p in folder.iterdir() if p.is_file()}
        results[case]=report
        print(case,{k:v for k,v in report.items() if k!='artifacts_sha256'},flush=True)
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='AUDITED',scope=__doc__,runs=results,
        binary_sha256=identity,script_sha256=digest(Path(__file__)),full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
