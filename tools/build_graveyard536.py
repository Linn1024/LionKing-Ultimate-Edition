"""Build live bone-platform colors, retaining the prepared vulture artwork policy."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard493.py')
s=template.read_text().replace("base=ROOT/'build/cant-wait482'","base=ROOT/'build/graveyard530'").replace("out=ROOT/'build/graveyard493'","out=ROOT/'build/graveyard536'")
s=s.replace("'engine/runner/tlk_wide.c',", "'engine/runner/tlk_wide.c','engine/runner/tlk_graveyard_bone_metadata.h',")
exec(compile(s,str(template),'exec'))
