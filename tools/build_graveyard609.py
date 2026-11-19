"""Observe a single real bone store on either execution path without replaying it after a yield."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait550.py')
s=template.read_text().replace("base=ROOT/'build/graveyard536'","base=ROOT/'build/graveyard599'").replace("out=ROOT/'build/cant-wait550'","out=ROOT/'build/graveyard609'")
s=s.replace("'engine/runner/tlk_audio.h',", "'engine/runner/tlk_audio.h','engine/runner/tlk_graveyard_audio_metadata.h',")
exec(compile(s,str(template),'exec'))
