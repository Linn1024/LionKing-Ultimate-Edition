"""Run all native route endpoints on the separate lizard-launch player."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_launch_native.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-launch2/player.exe'","ROOT/'build/pride-lizard-launch-work/player/player.exe'")
source=source.replace("ROOT/'build/pride-launch2/native-gates'","ROOT/'build/pride-lizard-launch-work/player/native-gates'")
exec(compile(source,str(original_verifier),'exec'))
