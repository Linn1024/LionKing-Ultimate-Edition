"""Build a read-only native DSP survey from the verified candidate graph."""
from pathlib import Path
original_verifier=Path(__file__).with_name('build_pride_bounce_loop_observer.py')
source=original_verifier.read_text().replace('bounce-loop-observer','bounce-dsp-observer')
source=source.replace('native_bounce_loop_observer.c','native_bounce_dsp_observer.c')
exec(compile(source,str(original_verifier),'exec'))
