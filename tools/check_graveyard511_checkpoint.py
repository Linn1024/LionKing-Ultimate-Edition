"""Author the fixture without the costly, unrelated widescreen presentation pass."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard510_checkpoint.py')
s=template.read_text().replace('build/graveyard510-checkpoint','build/graveyard511-checkpoint').replace("game = snes\\ndisplay.viewport = md\\n", "game = snes\\n")
s=s.replace('timeout=65','timeout=180').replace("with (out/'run.log').open('wb')", "env['SDL_VIDEODRIVER']='dummy'\nwith (out/'run.log').open('wb')")
s=s.replace('paths=[Path(__file__),reference', 'paths=[Path(__file__),template,reference')
exec(compile(s,str(template),'exec'))
