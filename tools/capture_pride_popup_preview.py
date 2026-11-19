"""Capture the current actual Windows popup with native/MD effect selections."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from verify_windows import pixels


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-popup-preview-baseline'
    out.mkdir()
    binary=ROOT/'build/pride-scene-template-work/player/native-engine/tlk_pride_player.exe'
    assert digest(binary)=='0f164e40902b08100c7012a3ab28e23e84aa6a106b047eee77c2e0487420c5c7'
    config=out/'host.ini'
    config.write_text('opengl = 0\nscale = 3\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    observations=[]
    commands=[]
    for field in (1664,1680,1688):
        images=[]
        for source in ('snes','md'):
            folder=out/f'{field}-{source}'
            folder.mkdir()
            profile=folder/'resources.ini'
            profile.write_text(f'schema = 1\ngame = snes\ngraphics.sprites.effects = {source}\n')
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc',
                 '--md-rom',ROOT/'Lion King, The (World).md','--config',config,
                 '--resource-profile',profile,'--input-polled',tape,'--frames',field,
                 '--no-pace','--no-audio','--no-record',
                 '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
            commands.append(list(map(str,cmd)))
            with (folder/'run.log').open('wb') as log:
                subprocess.run(commands[-1],cwd=ROOT,env=env,stdout=log,
                               stderr=subprocess.STDOUT,timeout=120,check=True)
            scene=json.loads((folder/'scene.json').read_text())
            pieces=[p for p in scene['pieces'] if p['fixed'] and p['kept']
                    and 0xc6fd06<=p['pose']<=0xc6fe9d]
            assert pieces, (field,source,'Expected visible native popup')
            images.append(pixels(folder/'window.png'))
            observations.append(dict(field=field,source=source,pieces=pieces))
        assert images[0]==images[1], 'Expected current unclassified effect gap changed'
        print(field,'actual clients identical under both effect choices',flush=True)
    paths=[Path(__file__),binary,ROOT/'engine/runner/tlk_wide.c',
           ROOT/'engine/runner/tlk_md_sprites.c',tape]
    artifacts={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}
    report=dict(result='POPUP_SOURCE_SELECTION_GAP_REPRODUCED',commands=commands,
                observations=observations,actual_sdl_client_captures=True,
                original_md_art_not_selected=True,production_changes=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256=artifacts)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
