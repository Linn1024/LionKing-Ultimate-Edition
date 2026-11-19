"""Compare the first real Windows frame after a private controller load."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-scene-state';out=base/'first-frame';out.mkdir(exist_ok=True)
    binary=base/'scene-state-sdl.exe';identity=digest(binary);results={}
    config=base/'windows/host.ini';profile=base/'windows/resources.ini'
    for mode in ('aot','lle'):
        cases={}
        for part in ('baseline','resumed'):
            folder=out/(mode+'-'+part);folder.mkdir(exist_ok=True);env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):env[key]=str(folder)
            for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                        'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO'):env[key]='1'
            env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
            inputs=base/'neutral.polled.tape' if part=='resumed' else ROOT/'build/pride-health-death-native/neutral-tail.polled.tape'
            command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--config',config,'--resource-profile',profile,'--frames','4704','--no-pace','--no-audio','--no-record',
                '--input-polled',inputs,'--dump-window',folder/'window.png','--wav',folder/'audio.wav','--wav-seconds','100']
            if part=='resumed':command+=['--load',base/'windows'/(mode+'.private-state')]
            if mode=='lle':command.append('--lle')
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            cases[part]=dict(guest=hashes(folder/'run.log'),artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        a=out/(mode+'-baseline');b=out/(mode+'-resumed')
        exact=pixels(a/'window.png')==pixels(b/'window.png') and cases['baseline']['guest']==cases['resumed']['guest']
        results[mode]=dict(runs=cases,first_displayed_frame_and_guest_exact=exact,
            exact_client_pixels=512*448 if exact else 0)
        print(mode+' first resumed Windows frame/guest exact='+str(exact),flush=True)
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='AUDITED',scope=__doc__,runs=results,
        binary_sha256=identity,script_sha256=digest(Path(__file__)),prepared_graphics_verified=False,
        full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
