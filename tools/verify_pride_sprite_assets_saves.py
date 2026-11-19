"""Verify actual sprite installation, damaged-data rejection and cold saves."""
from pathlib import Path

original = Path(__file__).with_name('verify_pride_installed_cache_setup.py')
source = original.read_text()

def change(before, after):
    global source
    assert source.count(before) == 1, before
    source = source.replace(before, after)

change("base = ROOT/'build/pride-installed-cache41'", "base = ROOT/'build/pride-sprite-fresh44'")
change("source = base/'verification/report.json'", "source = base/'runtime-verification/report.json'")
change("base/'verification/Game data & scene cache/scenes-v1.cache'", "base/'runtime-verification/Game data & scene cache/scenes-v1.cache'")
change("template[template.index('--asset-cache')+1] = str(cache)",
       "template[template.index('--asset-cache')+1] = str(cache)\n    template[template.index('--hud-assets')+1] = str(data/first['hud_assets']['file'])\n    template[template.index('--sprite-assets')+1] = str(data/first['sprite_assets']['file'])")
change("    state_hash = digest(seed/'saved.state')", """    previous = ROOT/'build/pride-installed-cache41/setup-verification/seed/saved.state'
    previous_template = ROOT/'build/pride-installed-cache41/setup-verification/report.json'
    bound(previous_template)
    previous_loaded, previous_rc, previous_text = run('previous41-cold', 1600, ['--load', previous], suffix)
    checks['previous41_save_loads_with_prepared_hud'] = previous_rc == 0 and 'loaded_state=' in previous_text
    state_hash = digest(seed/'saved.state')""")
change("('roms', 'scene_cache', 'menu_assets', 'native_final_assets', 'title_bank_assets'))",
       "('roms', 'scene_cache', 'menu_assets', 'native_final_assets', 'title_bank_assets', 'hud_assets', 'sprite_assets'))")
change("    checks['saved_state_still_unchanged']", """    checks['previous41_guest_preserved'] = hashes(previous_loaded/'run.log') == hashes(cold/'run.log')
    for name in ('window.png', 'scene.json', 'audio.wav'):
        checks['previous41_'+name+'_preserved'] = digest(previous_loaded/name) == digest(cold/name)
    checks['saved_state_still_unchanged']""")
change('paths = [Path(__file__), build_path, source,',
       "paths = [Path(__file__), original, build_path, source, previous, previous_template, ROOT/'dist/PrepareHudAssets.exe',")

exec(compile(source, str(original), 'exec'))
