"""Author the current player's ordinary normal-mode prefatal Continue snapshot."""
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-final-continue-fixture';out.mkdir()
    binary=ROOT/'build/pride-arena-work/tlk_pride_player.exe'
    original=ROOT/'build/pride-game-over-music/normal.tape';fatal=3894
    tape=out/'neutral-after-final.tape';tape.write_bytes(original.read_bytes()[:fatal*2]+bytes(1600))
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    state=out/'prefatal.state';cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--config',config,'--resource-profile',profile,'--input',tape,'--frames',fatal-1,'--save-at',fatal-1,state,
        '--no-pace','--no-audio','--no-record','--dump-window',out/'window.png','--dump-scene',out/'scene.json']
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    with (out/'run.log').open('wb') as log:
        subprocess.run(list(map(str,cmd)),cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    scene=json.loads((out/'scene.json').read_text());game=scene['latched_gameplay']
    assert game['health']==1 and game['lives']==0 and game['descriptor']==0x387,game
    paths=[Path(__file__),binary,original]
    report=dict(result='AUTHORED',fatal_field=fatal,gameplay=game,command=list(map(str,cmd)),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Normal-mode prefatal snapshot',game,flush=True)


if __name__=='__main__':main()
