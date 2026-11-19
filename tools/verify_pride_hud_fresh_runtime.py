"""Run the prepared-HUD installation/playback suite on the fresh CMake graph."""
from pathlib import Path

previous = Path(__file__).with_name('verify_pride_hud_assets_runtime.py')
source = previous.read_text()
before = "ROOT/'build/pride-hud-assets42/runtime-verification'"
assert source.count(before) == 1
source = source.replace(before, "ROOT/'build/pride-hud-fresh43/runtime-verification'")
before = "len(build['link_inputs_sha256']) == 322 and build['unchanged_prior_inputs'] == 318"
assert source.count(before) == 1
source = source.replace(before, "len(build['link_inputs_sha256']) == 322 and build['fresh_standalone_graph_claimed'] and not build['old_objects_or_archives_imported']")
source = source.replace("checks['three_prior_objects_changed_and_one_reader_added']", "checks['all322_link_inputs_fresh']")
before = "paths = [Path(__file__), original, build_path, old_build_path, source, ROOT/'build/pride-hud-assets/hud.assets'"
assert source.count(before) == 1
source = source.replace(before, "paths = [Path(__file__), original, ROOT/'tools/verify_pride_hud_assets_runtime.py', build_path, old_build_path, source, ROOT/'build/pride-hud-assets/hud.assets'")
exec(compile(source, str(previous), 'exec'))
