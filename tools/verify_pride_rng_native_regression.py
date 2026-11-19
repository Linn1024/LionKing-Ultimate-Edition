"""Keep preceding source-off native/mixed/death playback exact after forwarding."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_scene_save_regression.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-launch3'","ROOT/'build/pride-rng-player'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))
