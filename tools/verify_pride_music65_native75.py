"""Native gameplay endpoints after physical music-tail correction."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_installed_native75.py')
source=original.read_text().replace("ROOT/'build/pride-installed-cache41'", "ROOT/'build/pride-music-output65'")
source=source.replace("base/'verification/Game data & scene cache/scenes-v1.cache'", "ROOT/'build/pride-sprite-fresh44/runtime-verification/Game data & scene cache/scenes-v1.cache'")
anchor="'--md-rom', str(ROOT/'Lion King, The (World).md'), '--asset-cache', str(cache),"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\n               '--hud-assets', str(ROOT/'build/pride-hud-assets/hud.assets'),\n               '--sprite-assets', str(ROOT/'build/pride-continue-token-assets/sprites.assets'),")
source=source.replace('max_workers=4','max_workers=3')
source=source.replace('paths = [Path(__file__), build_path, source, cache, old_path]', "paths = [Path(__file__), original, build_path, source, cache, old_path, ROOT/'build/pride-hud-assets/hud.assets']")
exec(compile(source,str(original),'exec'))
