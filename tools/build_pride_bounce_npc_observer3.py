"""Build the read-only original NPC action observer from the verified graph."""
from pathlib import Path

original_verifier=Path(__file__).with_name('build_pride_bounce_loop_observer.py')
source=original_verifier.read_text().replace('bounce-loop-observer','bounce-npc-observer3')
source=source.replace('native_bounce_loop_observer.c','native_bounce_npc_observer3.c')
exec(compile(source,str(original_verifier),'exec'))
