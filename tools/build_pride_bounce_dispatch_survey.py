"""Build a read-only broad dispatch survey before choosing an NPC seam."""
from pathlib import Path
original_verifier=Path(__file__).with_name('build_pride_bounce_loop_observer.py')
source=original_verifier.read_text().replace('bounce-loop-observer','bounce-dispatch-survey')
source=source.replace('native_bounce_loop_observer.c','native_bounce_dispatch_survey.c')
exec(compile(source,str(original_verifier),'exec'))
