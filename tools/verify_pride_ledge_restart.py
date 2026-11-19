"""Switch ledge audio in the actual tree and compare both restarts to cold boots."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_arrival_restart.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-arrival-work/player'","ROOT/'build/pride-ledge-work/player'")
source=source.replace("out=base/'arrival-restart2'","out=base/'ledge-restart2'")
source=source.replace('audio.effects.world.pickup_arrival','audio.effects.simba.ledge_grab')
source=source.replace('from summarize_pride_practice import bound','from pride_ledge_history import bound')
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,ROOT/'tools/pride_ledge_history.py',bp,")
exec(compile(source,str(original_verifier),'exec'))
