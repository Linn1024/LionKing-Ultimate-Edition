"""Validate frozen evidence against the preserved decoder-template source."""
from pathlib import Path

original=Path(__file__).with_name('pride_bounce_owner_preview_history.py')
source=original.read_text()
needle="'pride-ledge-baseline','pride-lizard-launch-baseline','pride-bounce-owner-baseline'):"
assert source.count(needle)==1
source=source.replace(needle,"'pride-ledge-baseline','pride-lizard-launch-baseline','pride-bounce-owner-baseline','pride-scene-template-baseline'):")
exec(compile(source,str(original),'exec'))
