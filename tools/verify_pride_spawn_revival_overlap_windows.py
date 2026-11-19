"""Verify real SDL counter/cub overlap with native HUD explicitly kept in place."""
import array
import json
import os
from pathlib import Path
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_prepared_state import frame_records
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-spawn-revival';out=base/'overlap-windows';out.mkdir(exist_ok=True)
    binary=base/'spawn-revival-sdl.exe';identity=digest(binary);runs={};sources={}
    sources['build/pride-spawn-revival/build-report.json']=digest(base/'build-report.json')
    for field in (2072,3000):
        previous=None
        for mode in ('aot','lle'):
            name=f'{mode}-{field}';folder=out/name;folder.mkdir(exist_ok=True)
            reference=base/f'default/md-320-native-{mode}';profile=reference/'resources.ini';tape=reference/'default-neutral.tape'
            for p in (profile,tape):sources[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
            config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\nwidescreen_hud = in place\n')
            env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
            for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                        'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
            env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
            command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--resource-profile',profile,'--config',config,'--input',tape,'--frames',field,
                '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
                '--wav',folder/'audio.wav','--wav-seconds','100']
            if mode=='lle':command.append('--lle')
            with (folder/'run.log').open('wb') as log:
                result=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
            assert result.returncode==0,(name,result.returncode)
            w,h,client=pixels(folder/'window.png');assert (w,h)==(640,448)
            if field==2072:
                record=frame_records(reference/'render-owned.rgb',320)[295];colors=array.array('I');colors.frombytes(record[-320*224*4:])
                assert all(client[y*w+x]==(colors[y//2*320+x//2]>>16&255,colors[y//2*320+x//2]>>8&255,colors[y//2*320+x//2]&255) for y in range(h) for x in range(w))
            else:
                rw,rh,expected=pixels(reference/'picture.png')
                assert all(client[y*w+x]==expected[y//2*rw+x//2] for y in range(h) for x in range(w))
                assert hashes(folder/'run.log')==hashes(reference/'run.log')
            with wave.open(str(folder/'audio.wav'),'rb') as wav:
                assert wav.getnframes()==field*48000*357366//21477272;pcm=wav.readframes(wav.getnframes())
            actual=(hashes(folder/'run.log'),client,pcm)
            if previous:assert previous==actual
            previous=actual
            runs[name]=dict(exit_code=result.returncode,guest=hashes(folder/'run.log'),client_pixels=w*h,
                artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
            print('Native HUD in-place overlap '+name+' client/guest/PCM PASS',flush=True)
    sources['tools/verify_pride_spawn_revival_overlap_windows.py']=digest(Path(__file__))
    for name,sha in sources.items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='PASS',scope=__doc__,runs=runs,
        binary_sha256=identity,source_sha256=sources,full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
