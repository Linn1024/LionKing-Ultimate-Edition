"""Run all native route endpoints on the fresh fallback-repair candidate."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_launch_native.py')
source=original.read_text().replace("ROOT/'build/pride-launch2/player.exe'","ROOT/'build/pride-scene-template-work/player/player.exe'")
source=source.replace("ROOT/'build/pride-launch2/native-gates'","ROOT/'build/pride-scene-template-work/player/native-gates'")
exec(compile(source,str(original),'exec'))
