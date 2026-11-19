"""Build independently guarded second-level Continue audio, keeping artwork scope intact."""
from pathlib import Path
template=Path(__file__).with_name('build_cant_wait550.py')
s=template.read_text().replace("base=ROOT/'build/graveyard536'","base=ROOT/'build/cant-wait572'").replace("out=ROOT/'build/cant-wait550'","out=ROOT/'build/cant-wait579'")
s=s.replace("'engine/runner/tlk_audio.h',", "'engine/runner/tlk_audio.h','engine/runner/tlk_cw_audio_metadata.h',")
exec(compile(s,str(template),'exec'))
