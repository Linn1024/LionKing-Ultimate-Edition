"""Build a read-only original accepted-queue observer from the public graph."""
from pathlib import Path
original_verifier=Path(__file__).with_name('build_pride_bounce_loop_observer.py')
source=original_verifier.read_text().replace('bounce-loop-observer','audio-queue-owner-observer')
source=source.replace('native_bounce_loop_observer.c','native_audio_queue_owner_observer.c')
exec(compile(source,str(original_verifier),'exec'))
