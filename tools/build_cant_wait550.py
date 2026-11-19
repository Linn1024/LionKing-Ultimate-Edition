"""Build scoped second-level roar support and its independent effect-tail owner."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard493.py')
s=template.read_text().replace("base=ROOT/'build/cant-wait482'","base=ROOT/'build/graveyard536'").replace("out=ROOT/'build/graveyard493'","out=ROOT/'build/cant-wait550'")
s=s.replace("('wide',b['compiles']['wide'],None)", "('audio',b['compiles']['audio'],out/'game/tlk_audio.c')")
s=s.replace("'engine/runner/tlk_wide.c',", "'engine/runner/tlk_audio.c','engine/runner/tlk_audio.h',")
exec(compile(s,str(template),'exec'))
