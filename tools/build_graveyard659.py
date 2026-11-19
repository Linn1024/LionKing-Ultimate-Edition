"""Use verified native music ownership in Graveyard; add a read-only skull-actor trace."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard635.py')
s=template.read_text().replace("base=ROOT/'build/graveyard621'", "base=ROOT/'build/graveyard652'").replace("out=ROOT/'build/graveyard635'", "out=ROOT/'build/graveyard659'")
s=s.replace("('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),", "('graveyard_gameplay',b['compiles']['graveyard_gameplay'],ROOT/'engine/runner/tlk_graveyard_gameplay.c'),")
s=s.replace("'engine/runner/tlk_audio.c',", "'engine/runner/tlk_audio.c','engine/runner/tlk_graveyard_gameplay.c',")
exec(compile(s,str(template),'exec'))
