"""Exercise the excluded native-art final fade through actual Windows clients."""
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels,hashes


def main():
    base=ROOT/'build/pride-final-scene-probe3';out=base/'capture';out.mkdir()
    build=bound(base/'build-report.json');binary=base/'player.exe';assert digest(binary)==build['binary_sha256']
    state=ROOT/'build/pride-final-presentation/preview/prefatal.state';identity=digest(state)
    tape=ROOT/'build/pride-final-presentation/preview/ordinary.tape'
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[];observations=[];checks={}
    for mode,offsets in [('control',(0,88,436)),('candidate',(0,4,8,16,19,24,88,96,100,104,118,120,121,144))]:
        for offset in offsets:
            folder=out/f'{mode}-{offset}';folder.mkdir()
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',profile,'--config',config,'--input',tape,'--load',state,'--lle','--frames',2369+offset,
                 '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
                 '--dump-png',folder/'native.png','--dump-scene',folder/'scene.json']
            commands.append(list(map(str,cmd)));enabled=str(int(mode=='candidate'))
            env=dict(clean,TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP=enabled,
                     TLK_FINAL_FAST_ASSETS=enabled,TLK_FINAL_SCENE_PRESENT=enabled)
            with (folder/'run.log').open('wb') as log:
                subprocess.run(commands[-1],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            w,h,data=pixels(folder/'window.png');scene=json.loads((folder/'scene.json').read_text())
            row=dict(mode=mode,offset=offset,nonblack=sum(p!=(0,0,0) for p in data),peak=max(max(p) for p in data),pieces=len(scene['pieces']))
            observations.append(row);print(row,flush=True)
            if mode=='control':
                reference=ROOT/'build/pride-final-presentation/preview'/str(offset)
                checks[f'control/{offset}/same_guest']=hashes(folder/'run.log')==hashes(reference/'run.log')
                checks[f'control/{offset}/same_window']=pixels(folder/'window.png')==pixels(reference/'window.png')
    first=pixels(out/'candidate-0/native.png');target=pixels(out/'candidate-100/native.png')
    rw,rh,reference=pixels(ROOT/'build/pride-late-visible/102/window.png')
    full_target=[reference[y*2*rw+x*2] for y in range(224) for x in range(256)]
    checks['target_is_complete_before_visible_phase']=target[2]==full_target
    for row in observations:
        if row['mode']!='candidate' or row['offset']>=121:continue
        age=row['offset'];data=first[2] if age<25 else target[2];expected=[]
        for p in data:
            colour=[]
            for v in p:
                c=v>>3
                if age<25:c=max(0,c-(age+2)//3*4)
                elif age<97:c=0
                else:c=min(c,(age-97)//3*4)
                colour.append(c*8+(c>>2))
            expected.append(tuple(colour))
        w,h,actual=pixels(out/f'candidate-{age}/window.png')
        checks[f'candidate/{age}/display_fade']=w==512 and h==448 and all(actual[(y*2)*w+x*2]==expected[y*256+x] for y in range(224) for x in range(256))
    checks['original_save_retained']=digest(state)==identity
    paths=[Path(__file__),base/'build-report.json',binary,state,tape]
    report=dict(result='PROTOTYPE_PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        native_art_only=True,neutral_post_hit_input_only=True,interpreter_only=True,public_player_changed=False,
        mixed_source_masks_audio_and_lifecycle_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'final scene checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
