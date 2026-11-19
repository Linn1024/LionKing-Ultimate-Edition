"""Measure actual destination readiness after the excluded late final-life bypass."""
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    out=ROOT/'build/pride-late-visible';out.mkdir()
    probe=ROOT/'build/pride-bounce-owner-work/player/final-skip-late-probe'
    build=bound(probe/'build-report.json');binary=probe/'player.exe'
    assert digest(binary)==build['binary_sha256']
    state=ROOT/'build/pride-final-presentation/preview/prefatal.state';identity=digest(state)
    tape=ROOT/'build/pride-final-presentation/preview/ordinary.tape'
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[];observations=[]
    def capture(offset):
        folder=out/str(offset);folder.mkdir()
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input',tape,'--load',state,'--lle','--frames',2369+offset,
             '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
        commands.append(list(map(str,cmd)))
        env=dict(clean,TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1')
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        w,h,data=pixels(folder/'window.png');scene=json.loads((folder/'scene.json').read_text())
        row=dict(offset=offset,nonblack=sum(p!=(0,0,0) for p in data),peak=max(max(p) for p in data),
                 width=w,height=h,gameplay=scene['latched_gameplay'])
        observations.append(row);print(row,flush=True);return row
    for offset in (88,96,100,104,112,120,128,144,160):capture(offset)
    black=max(r['offset'] for r in observations if r['nonblack']==0)
    visible=min(r['offset'] for r in observations if r['offset']>black and r['nonblack'])
    while visible-black>1:
        middle=(black+visible)//2;row=capture(middle)
        if row['nonblack']:visible=middle
        else:black=middle
    assert digest(state)==identity
    paths=[Path(__file__),probe/'build-report.json',binary,state,tape]
    report=dict(result='MEASURED',first_visible_video_offset=visible,last_black_video_offset=black,
        observations=sorted(observations,key=lambda r:r['offset']),commands=commands,
        excluded_interpreter_experiment=True,public_player_changed=False,final_life_adapter_implemented=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Late-bypass first visible destination offset',visible,flush=True)


if __name__=='__main__':main()
