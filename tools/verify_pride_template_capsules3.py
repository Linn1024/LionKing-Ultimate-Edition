"""Verify capsule retention with invocation-serial-based observation."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_template_capsules.py')
source=original.read_text()
needle="ROOT/'build/pride-bounce-owner-work/player/fallback-probe2'"
assert source.count(needle)==1
source=source.replace(needle,"ROOT/'build/pride-bounce-owner-work/player/fallback-probe3'")
source=source.replace('paths=[Path(__file__),bp,','paths=[Path(__file__),original,bp,')
exec(compile(source,str(original),'exec'))
