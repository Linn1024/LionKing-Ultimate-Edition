"""Locate the actual owned revival on ordinary input before caption comparisons."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-title-reentry';out.mkdir()
    binary=ROOT/'build/pride-title-work/player/native-engine/tlk_pride_player.exe'
    assert digest(binary)=='fdc9df37db7c912f39c0c6484441e057f066259564655e03f67f28a39fa17f9e'
    original=ROOT/'build/pride-scene-template-work/player/owned-regression/mixed.ini'
    profile=out/'resources.ini';profile.write_text(original.read_text()+'\ngraphics.titles.pride_lands = md\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 3\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
         '--config',config,'--resource-profile',profile,'--input',tape,'--frames',3000,
         '--no-pace','--no-audio','--no-record','--dump-window',out/'window.png','--dump-scene',out/'scene.json']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env['TLK_PRIDE_DIAGNOSTICS']=str(out)
    with (out/'run.log').open('wb') as log:
        subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    paths=[Path(__file__),binary,original,tape]
    report=dict(result='REENTRY_ROUTE_CAPTURED',command=list(map(str,cmd)),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sorted(report['artifacts_sha256']),flush=True)


if __name__=='__main__':main()
