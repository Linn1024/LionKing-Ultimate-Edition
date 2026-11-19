"""Build the complete sound-owner family and guest-derived pending reaction reconstruction."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait550.py')
s=template.read_text().replace("base=ROOT/'build/graveyard536'","base=ROOT/'build/cant-wait555'").replace("out=ROOT/'build/cant-wait550'","out=ROOT/'build/cant-wait560'")
s=s.replace("'engine/runner/tlk_audio.h',", "'engine/runner/tlk_audio.h','engine/runner/tlk_cw_audio_metadata.h',")
exec(compile(s,str(template),'exec'))
