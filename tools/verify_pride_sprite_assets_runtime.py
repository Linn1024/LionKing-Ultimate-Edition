"""Verify strict prepared-sprite playback against the retained renderer."""
from pathlib import Path

original = Path(__file__).with_name('verify_pride_installed_cache.py')
source = original.read_text().replace('OTHER_RESOURCE_PREP_CALLED', 'ROM_SPRITE_CALLED')

def change(before, after):
    global source
    assert source.count(before) == 1, before
    source = source.replace(before, after)

change("out = ROOT/'build/pride-installed-cache41/verification'", "out = ROOT/'build/pride-sprite-fresh44/runtime-verification'")
change('paths = [Path(__file__), build_path, old_build_path, source]',
       "paths = [Path(__file__), original, build_path, old_build_path, source, ROOT/'build/pride-hud-assets/hud.assets', ROOT/'build/pride-hud-assets/verification/report.json']")
change('debugger=None, full_hashes=False):', 'debugger=None, full_hashes=False, hud=None, sprites=None):')
change("if cached is not None: cmd += ['--asset-cache', str(cached)]", """if cached is not None: cmd += ['--asset-cache', str(cached)]
        if not old and hud is not False:
            cmd += ['--hud-assets', str(ROOT/'build/pride-hud-assets/hud.assets' if hud is None else hud)]
        if not old and sprites is not False:
            cmd += ['--sprite-assets', str(ROOT/'build/pride-sprite-assets/sprites.assets' if sprites is None else sprites)]""")
change("    failed, rc, text = run('prepare-failure'", """    hud_record = (ROOT/'build/pride-hud-assets/hud.assets').read_bytes()
    hud_cases = {'missing_argument': False, 'empty_argument': '', 'missing_file': out/'missing-hud.assets'}
    for label, offset in [('bad_version', 8), ('bad_source', 16), ('bad_digest', 80), ('bad_payload', 112)]:
        damaged_hud = bytearray(hud_record); damaged_hud[offset] ^= 1
        path = out/(label+'.hud.assets'); path.write_bytes(damaged_hud); hud_cases[label] = path
    for label, path in hud_cases.items():
        folder, rc, text = run('reject-hud-'+label, cached=cache, hud=path)
        checks['hud-'+label+'_stops_before_guest'] = (rc == 8 and 'Installed HUD data is missing or incompatible.' in text
            and 'frame_sha256=' not in text and not (folder/'window.png').exists() and not (folder/'audio.wav').exists())
    failed, rc, text = run('prepare-failure'""")
change('break SnesInit\ncommands', '''break TlkMdHudInit
commands
silent
printf "ROM_HUD_CALLED\\\\n"
continue
end
break TlkMdHudInitPrepared
commands
silent
printf "PREPARED_HUD_CALLED\\\\n"
continue
end
break SnesInit
commands''')
change("    checks['other_startup_asset_migration_still_needed'] = 'ROM_SPRITE_CALLED' in text", """    checks['prepared_hud_used_without_rom_hud_initialization'] = 'PREPARED_HUD_CALLED' in text and 'ROM_HUD_CALLED' not in text
    hud_failure, rc, failed_text = run('missing-hud-debugger', cached=cache, hud=False, debugger=script)
    checks['missing_hud_never_initializes_guest_or_hud'] = rc == 0 and not any(marker in failed_text for marker in ('GUEST_INIT_CALLED', 'ROM_HUD_CALLED', 'PREPARED_HUD_CALLED'))
    checks['sprites_prepared_without_rom_decode_or_bind'] = 'PREPARED_SPRITE_CALLED' in text and 'ROM_SPRITE_CALLED' not in text and 'ROM_SPRITE_BIND_CALLED' not in text""")
change("checks['only_two_of_321_inputs_changed'] = len(build['link_inputs_sha256']) == 321 and build['unchanged_link_inputs'] == 319",
       "checks['all322_inputs_fresh'] = len(build['link_inputs_sha256']) == 322 and build['fresh_standalone_graph_claimed'] and not build['old_objects_or_archives_imported']")

change('break SnesInit\ncommands', """break TlkMdSpriteAssetsActivate
commands
silent
printf "PREPARED_SPRITE_CALLED\\\\n"
continue
end
break TlkMdSpritesBindSnes
commands
silent
printf "ROM_SPRITE_BIND_CALLED\\\\n"
continue
end
break SnesInit
commands""")
change("    failed, rc, text = run('prepare-failure'", """    sprite_record = (ROOT/'build/pride-sprite-assets/sprites.assets').read_bytes()
    sprite_cases = {'missing_argument': False, 'empty_argument': '', 'missing_file': out/'missing-sprites.assets'}
    for label, offset in [('bad_version', 8), ('bad_source', 24), ('bad_policy', 88), ('bad_digest', 120), ('bad_payload', 192)]:
        damaged_sprite = bytearray(sprite_record); damaged_sprite[offset] ^= 1
        path = out/(label+'.sprites.assets'); path.write_bytes(damaged_sprite); sprite_cases[label] = path
    for label, path in sprite_cases.items():
        folder, rc, text = run('reject-sprites-'+label, cached=cache, sprites=path)
        checks['sprites-'+label+'_stops_before_guest'] = (rc == 8 and 'Installed sprite data is missing or incompatible.' in text
            and 'frame_sha256=' not in text and not (folder/'window.png').exists() and not (folder/'audio.wav').exists())
    failed, rc, text = run('prepare-failure'""")
change('paths = [Path(__file__), original,', "paths = [Path(__file__), original, ROOT/'build/pride-sprite-assets/sprites.assets', ROOT/'build/pride-sprite-assets/verification/report.json',")
exec(compile(source, str(original), 'exec'))
