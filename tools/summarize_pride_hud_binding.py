"""Bind the shipped HUD fix and fresh regressions, retaining historical scene research."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def log_text(path):
    raw = path.read_bytes()
    return raw.decode('utf-16' if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else 'utf-8')


def main():
    out = ROOT / 'build/pride-hud-rebinding'
    player = 'd49a9374c73795e5885e7e0e7f0977bd172222e5c8a813e3006982c51719788b'
    headless = '9a1c5953d571b889ae55bd54477c8cc458856f84f44f95aae9b0144a5c664af6'
    assert digest(ROOT/'dist/LionKing.exe') == digest(ROOT/'engine/build-win/tlk_sdl.exe') == player
    assert digest(ROOT/'engine/build-win/tlk_headless.exe') == headless
    bound = {}
    def load(name, relative):
        path = ROOT / relative
        report = json.loads(path.read_text())
        assert report['result'] == 'PASS', (name, report.get('result'))
        bound[name] = {'path': relative, 'sha256': digest(path)}
        return report
    hud = load('hud', 'build/pride-hud-rebinding/report.json')
    assert hud['candidate_sha256'] == player and hud['after_reload_changed_pixels'] == 2096
    for name, sha in hud['source_sha256'].items():
        assert digest(ROOT/name) == sha, name
    for name, sha in hud['artifacts_sha256'].items():
        assert digest(out/name) == sha, name
    state = load('checkpoint_state', 'build/pride-hud-rebinding/state-report.json')
    assert state['player_sha256'] == player and state['relocated_hud_window_and_complete_pcm_tail_exact']
    assert state['cross_graphics_native_fallback_exact']
    assert state['source_sha256'] == digest(ROOT/'tools/verify_pride_hud_checkpoint_state.py')
    assert state['hud_gate_sha256'] == digest(out/'report.json')
    assert state['state_sha256'] == digest(out/'checkpoint.state')
    play = load('native_routes', 'build/native-route-verification/play-report.json')
    assert play['route_count'] == 75 and '75 native AOT/LLE routes PASS' in log_text(out/'native.log')
    bugs = load('allbugs', 'build/native-route-verification/allbugs-report.json')
    assert bugs['allbugs_tracked_ram_equal_every_frame']
    assert '1 native AOT/LLE routes PASS' in log_text(out/'allbugs.log')
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes() == (ROOT/'build/native-route-verification/allbugs-lle.ram').read_bytes()
    for scenario in ('gameplay', 'gameplay256', 'media', 'media256'):
        report = load(scenario, 'build/pride-authored-completion/'+scenario+'/report.json')
        assert report['headless_sha256'] == headless
        if scenario.startswith('media'):
            assert report['player_sha256'] == player
        assert report['normal_first_level_completion_verified'] and not report['loaded_states'] and not report['actor_or_world_edits']
    ui = load('ui', 'build/windows-smoke/report.json')
    assert ui['live_F10_round_trip'] and ui['unadapted_background_native_fallback']
    setup = load('installer', 'build/setup-verification/report.json')
    assert setup['actual_setup_window'] and setup['source_roms_settings_and_saves_unchanged']
    launch = load('launchers', 'build/next-level-launchers/report.json')
    assert len(launch['levels']) == 9
    assert 'remap_selftest: PASS (0 failed)' in log_text(out/'remap.log')
    assert 'actual Windows UI PASS' in log_text(out/'installer.log')
    assert log_text(out/'launchers.log').count('actual installed launch PASS') == 9
    historic_path = ROOT/'build/pride-scene-restore-latest.json'
    historic = json.loads(historic_path.read_text())
    assert historic['result'] == 'PARTIAL' and historic['canonical_original_revival_fields'] == 304
    assert not historic['production_death_behavior_enabled']
    result = dict(result='PARTIAL', scope=__doc__, production_sha256={'dist/LionKing.exe':player,
                  'engine/build-win/tlk_headless.exe':headless},
                  hud_checkpoint_role_binding_fixed=True, native_route_count=75,
                  checkpoint_cross_process_md_native_graphics_save_verified=True,
                  allbugs_tracked_rows=60648, healthy_completion_mode_runs=8,
                  installer_and_real_ui_verified=True, installed_later_level_launchers=9,
                  remapping_selftest_failed=0,
                  current_gate_reports=bound,
                  historical_scene_research={'path':str(historic_path.relative_to(ROOT)),
                      'sha256':digest(historic_path), 'runtime':'preceding95fa/9aa8, not replayed with HUD fix',
                      'research_source_unchanged':True, 'current_production_gate':False},
                  production_death_behavior_enabled=False, full_first_level_fidelity_complete=False,
                  remaining=historic['remaining'][1:],
                  source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in
                      (Path(__file__),ROOT/'engine/runner/tlk_hud_role.h',ROOT/'engine/runner/tlk_wide.c',
                       ROOT/'engine/tests/hud_role_test.c')},
                  unit_sha256={'exe':digest(out/'hud_role_test.exe'),'log':digest(out/'unit.log'),
                               'remap_log':digest(out/'remap.log')})
    (ROOT/'build/pride-hud-binding-latest.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Shipped checkpoint HUD binding, native75/All Bugs/eight completion runs/UI/installer/nine launchers verified; full Pride PARTIAL', flush=True)


if __name__ == '__main__':
    main()
