"""Verify private controller resumes through actual Windows clients and PCM.

The normal presenter is intentional here. Prepared scene presentation requires
additional history and is not certified by these controller lifecycle checks.
"""
import json
import os
from pathlib import Path
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes,pixels


def pcm(path):
    with wave.open(str(path),'rb') as wav:
        assert wav.getnchannels()==2 and wav.getframerate()==48000
        return wav.getnframes(),wav.readframes(wav.getnframes())


def main():
    base=ROOT/'build/pride-scene-state';out=base/'windows';out.mkdir(exist_ok=True)
    binary=base/'scene-state-sdl.exe';build_path=base/'build-report.json';identity=digest(binary)
    build=json.loads(build_path.read_text());assert identity==build['runs']['sdl']['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = snes\n')
    results={}
    for mode in ('aot','lle'):
        runs={};state=out/(mode+'.private-state')
        for part in ('baseline','resumed'):
            folder=out/(mode+'-'+part);folder.mkdir(exist_ok=True);env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):env[key]=str(folder)
            for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                        'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO'):env[key]='1'
            env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
            inputs=base/'neutral.polled.tape' if part=='resumed' else ROOT/'build/pride-health-death-native/neutral-tail.polled.tape'
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--config',config,'--resource-profile',profile,'--frames','5400','--no-pace','--no-audio','--no-record',
                 '--input-polled',inputs,'--dump-window',folder/'window.png','--wav',folder/'audio.wav','--wav-seconds','100']
            if mode=='lle':cmd.append('--lle')
            if part=='resumed':cmd+=['--load',state]
            else:cmd+=['--save-at','4703',state]
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            runs[part]=dict(guest=hashes(folder/'run.log'),artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        a=out/(mode+'-baseline');b=out/(mode+'-resumed')
        guest=runs['baseline']['guest']==runs['resumed']['guest'];window=pixels(a/'window.png')==pixels(b/'window.png')
        full_n,full=pcm(a/'audio.wav');tail_n,tail=pcm(b/'audio.wav')
        assert full_n==5400*48000*357366//21477272 and tail_n==(5400-4703)*48000*357366//21477272
        audio=full[-len(tail):]==tail
        results[mode]=dict(runs=runs,state_sha256=digest(state),guest_hashes_exact=guest,
            actual_client_exact=window,exact_client_pixels=512*448 if window else 0,
            continuation_pcm_exact=audio,continuation_pcm_bytes=len(tail),
            first_tail_difference=next((n for n,(x,y) in enumerate(zip(full[-len(tail):],tail)) if x!=y),None))
        print(mode+': guest='+str(guest)+'; actual window='+str(window)+'; continuation PCM='+str(audio),flush=True)
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='AUDITED',scope=__doc__,runs=results,
        binary_sha256=identity,source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__)),
        str(build_path.relative_to(ROOT)).replace('\\','/'):digest(build_path)},
        prepared_graphics_verified=False,full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
