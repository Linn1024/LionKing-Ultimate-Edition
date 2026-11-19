"""Build independent rhino/contact/reaction sounds with native reaction-driven voice lifetime."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait550.py')
s=template.read_text().replace("base=ROOT/'build/graveyard536'","base=ROOT/'build/cant-wait550'").replace("out=ROOT/'build/cant-wait550'","out=ROOT/'build/cant-wait555'")
s=s.replace("'engine/runner/tlk_audio.h',", "'engine/runner/tlk_audio.h','engine/runner/tlk_cw_monkey_metadata.h',")
exec(compile(s,str(template),'exec'))
