"""Run all native endpoint pairs on the fresh prepared-HUD CMake player."""
from pathlib import Path

original = Path(__file__).with_name('verify_pride_installed_native75.py')
source = original.read_text().replace("ROOT/'build/pride-installed-cache41'", "ROOT/'build/pride-hud-fresh43'")
source = source.replace("base/'verification/Game data & scene cache/scenes-v1.cache'",
                        "base/'runtime-verification/Game data & scene cache/scenes-v1.cache'")
before = "'--md-rom', str(ROOT/'Lion King, The (World).md'), '--asset-cache', str(cache),"
assert source.count(before) == 1
source = source.replace(before, before+"\n               '--hud-assets', str(ROOT/'build/pride-hud-assets/hud.assets'),")
source = source.replace('paths = [Path(__file__), build_path, source, cache, old_path]',
                        "paths = [Path(__file__), original, build_path, source, cache, old_path, ROOT/'build/pride-hud-assets/hud.assets']")
exec(compile(source, str(original), 'exec'))
