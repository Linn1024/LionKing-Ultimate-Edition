"""Build a read-only queue dispatch survey from the verified public graph."""
from pathlib import Path
original_verifier=Path(__file__).with_name('build_pride_bounce_loop_observer.py')
source=original_verifier.read_text().replace('bounce-loop-observer','audio-queue-dispatch-survey')
source=source.replace('native_bounce_loop_observer.c','native_audio_queue_dispatch_survey.c')
exec(compile(source,str(original_verifier),'exec'))
