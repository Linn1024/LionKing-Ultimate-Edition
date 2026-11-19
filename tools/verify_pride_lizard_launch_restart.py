"""Switch the independent launch choice in the real resource tree."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_arrival_restart.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-arrival-work/player'","ROOT/'build/pride-lizard-launch-work/player'")
source=source.replace("out=base/'arrival-restart2'","out=base/'launch-restart'")
source=source.replace('audio.effects.world.pickup_arrival','audio.effects.world.lizard_launch')
source=source.replace('from summarize_pride_practice import bound','from pride_lizard_launch_history import bound')
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,ROOT/'tools/pride_lizard_launch_history.py',bp,")
exec(compile(source,str(original_verifier),'exec'))
