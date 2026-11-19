"""Extend the retained installed-cache suite with prepared HUD playback checks."""
from pathlib import Path

original = Path(__file__).with_name('verify_pride_installed_cache.py')
source = original.read_text()

def change(before, after):
    global source
    assert source.count(before) == 1, before
    source = source.replace(before, after)

change("out = ROOT/'build/pride-installed-cache41/verification'", "out = ROOT/'build/pride-hud-assets42/runtime-verification'")
change('paths = [Path(__file__), build_path, old_build_path, source]',
       "paths = [Path(__file__), original, build_path, old_build_path, source, ROOT/'build/pride-hud-assets/hud.assets', ROOT/'build/pride-hud-assets/verification/report.json']")
change('debugger=None, full_hashes=False):', 'debugger=None, full_hashes=False, hud=None):')
change("if cached is not None: cmd += ['--asset-cache', str(cached)]", """if cached is not None: cmd += ['--asset-cache', str(cached)]
        if not old and hud is not False:
            cmd += ['--hud-assets', str(ROOT/'build/pride-hud-assets/hud.assets' if hud is None else hud)]""")
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
change("    checks['other_startup_asset_migration_still_needed']", """    checks['prepared_hud_used_without_rom_hud_initialization'] = 'PREPARED_HUD_CALLED' in text and 'ROM_HUD_CALLED' not in text
    hud_failure, rc, failed_text = run('missing-hud-debugger', cached=cache, hud=False, debugger=script)
    checks['missing_hud_never_initializes_guest_or_hud'] = rc == 0 and not any(marker in failed_text for marker in ('GUEST_INIT_CALLED', 'ROM_HUD_CALLED', 'PREPARED_HUD_CALLED'))
    checks['other_startup_asset_migration_still_needed']""")
change("checks['only_two_of_321_inputs_changed'] = len(build['link_inputs_sha256']) == 321 and build['unchanged_link_inputs'] == 319",
       "checks['three_prior_objects_changed_and_one_reader_added'] = len(build['link_inputs_sha256']) == 322 and build['unchanged_prior_inputs'] == 318")

exec(compile(source, str(original), 'exec'))
