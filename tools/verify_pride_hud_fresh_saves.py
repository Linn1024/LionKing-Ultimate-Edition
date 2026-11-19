"""Exercise actual prepared-data installation and cold saves on the fresh graph."""
from pathlib import Path

previous = Path(__file__).with_name('verify_pride_hud_assets_saves.py')
source = previous.read_text()
before = "ROOT/'build/pride-hud-assets42'"
assert source.count(before) == 1
source = source.replace(before, "ROOT/'build/pride-hud-fresh43'")
before = 'paths = [Path(__file__), original, build_path, source, previous, previous_template,'
assert source.count(before) == 1
source = source.replace(before, "paths = [Path(__file__), original, ROOT/'tools/verify_pride_hud_assets_saves.py', build_path, source, previous, previous_template,")
exec(compile(source, str(previous), 'exec'))
