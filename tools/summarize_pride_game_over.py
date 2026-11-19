"""Bind the current Pride game-over milestone without declaring full fidelity."""
import hashlib
import json
from pathlib import Path
import re
from audit_scenes import ROOT


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player = ROOT/'dist/LionKing.exe';headless = ROOT/'engine/build-win/tlk_headless.exe'
    ph, hh = digest(player), digest(headless)
    index = {}
    def read(name, result='PASS', fresh=True):
        path = ROOT/'build'/name
        value = json.loads(path.read_text(encoding='utf-8-sig'))
        assert value['result'] == result, (name, value['result'])
        if fresh:
            assert path.stat().st_mtime_ns >= max(player.stat().st_mtime_ns, headless.stat().st_mtime_ns), ('Stale report', name)
        if 'player_sha256' in value: assert value['player_sha256'] == ph, name
        if 'headless_sha256' in value: assert value['headless_sha256'] == hh, name
        index[name] = digest(path)
        return value
    original = read('pride-game-over-original/report.json', fresh=False)
    assert len(original['life_losses']) == 9 and original['no_430_on_final_life']
    assert all(r['level'] == 1 and r['health'] == 0 for r in original['life_losses'])
    assert int(original['game_over_music'][0]['value']) == 327
    music = read('pride-game-over-music/report.json')
    assert music['original_reference_sha256'] == digest(ROOT/'build/pride-game-over-original/report.json')
    assert music['ordinary_power_on_runs'] == 16 and len(music['saved_phases']) == 5
    assert music['final_life_no_430'] and music['normal_continue_accepted_and_level_restored']
    assert music['source_change_resets_md'] and music['same_program_sibling_is_independent']
    health = read('pride-health-death-music/report.json')
    assert health['ordinary_power_on_complete_runs'] == 8 and len(health['exact_saved_phases']) == 6
    assert health['living_v1_audio_exact'] and health['invalid_phase_rejected']
    fx = read('pride-death-fx-timeline/report.json')
    assert all(v['exact_timeline_advance'] for v in fx['cases'].values())
    for name, leaf in [('pride-game-over-switch','audio.music.pride_game_over'),
                       ('pride-health-death-switch','audio.music.pride_health_death')]:
        ui = read(name+'/report.json')
        assert ui['leaf'] == leaf and ui['both_directions_persisted'] and ui['original_loader_calls'] == 3
        assert ui['states'][0]['audio_fingerprint'] == ui['states'][2]['audio_fingerprint'] != ui['states'][1]['audio_fingerprint']
    active = read('pride-game-over-active/report.json')
    assert active['saved_track'] == 327 and active['menu_captured']
    read('final-music-switch/report.json')
    audio = read('pride-audio-state/report.json')
    assert audio['mixed_audio_aot_lle_exact'] and audio['actual_paused_voice_and_unpause']
    read('pride-audio-live-state/report.json')
    profiles = read('pride-state-profiles/report.json')
    assert profiles['mismatches_rejected_before_load'] == 32
    lifecycle = read('pride-death-lifecycle/report.json', 'COUNTER_CONVENTIONS_VERIFIED_DEATH_TIMING_OPEN')
    assert lifecycle['source_sha256']['native_headless'] == hh
    assert not lifecycle['counter_conventions']['raw_write_timing_alone_justifies_life_counter_patch']
    assert len(lifecycle['normalized_life_count_milestones']) == 3
    completions = {}
    for name in ('gameplay','gameplay256','media','media256'):
        value = read('pride-authored-completion/'+name+'/report.json')
        assert value['normal_first_level_completion_verified'] and not value['loaded_states'] and not value['actor_or_world_edits']
        assert value['execution_modes']['aot'] == value['execution_modes']['lle']
        completions[name] = value.get('exact_mixed_wav_sha256')
    play = read('native-route-verification/play-report.json')
    bugs = read('native-route-verification/allbugs-report.json')
    before = ROOT/'build/pride-game-over-native'
    assert play['route_count'] == 75 and play['routes'] == json.loads((before/'baseline-play-report.json').read_text())['routes']
    assert bugs['allbugs_tracked_ram_equal_every_frame']
    assert bugs['routes'] == json.loads((before/'baseline-allbugs-report.json').read_text())['routes']
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes() == (ROOT/'build/streaming-allbugs-before.ram').read_bytes()
    units = read('pride-game-over-native/unit-report.json')
    for name, expected in units['binary_sha256'].items():
        assert digest(ROOT/'engine/build-win'/(name+'.exe')) == expected
    assert digest(before/'unit.log') == units['log_sha256']
    installer = read('setup-verification/report.json')
    assert installer['actual_setup_window'] and installer['source_roms_settings_and_saves_unchanged']
    launchers = read('next-level-launchers/report.json')
    assert len(launchers['levels']) == 9
    manifest = json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'))
    assert manifest['player_sha256'] == ph
    cache_hash = digest(ROOT/'game-data/scenes-v1.cache')
    assert cache_hash == '94e6d05bad469ca7767ddd0878e2a5b057f379f99736744f471f89598d3c94d6'
    def log_text(path):
        raw = path.read_bytes()
        return raw.decode('utf-16' if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else 'utf-8')
    pytest = log_text(before/'pytest.log');mx = log_text(before/'exit-mx.log')
    assert '23 passed, 4 skipped' in pytest
    assert not re.search(r'^WRONG\s', mx, re.M) and len(re.findall(r'^UNPROVEN\s', mx, re.M)) == 11
    result = {'result': 'PARTIAL', 'scope': __doc__, 'player_sha256': ph, 'headless_sha256': hh,
              'reports_sha256': index, 'ordinary_game_over_continue_runs': 16,
              'game_over_exact_saved_phases': 5, 'nonfinal_death_exact_saved_phases': 6,
              'ordinary_supported_completion_runs': 8, 'canonical_media_wav_sha256': completions,
              'native_routes_unchanged': 75, 'tracked_allbugs_rows_unchanged': 60648,
              'cache_sha256': cache_hash, 'full_first_level_fidelity_complete': False,
              'remaining': ['Original death presentation/timers and fall gameplay differences',
                            'Remaining combat, enemy behavior and difficulty contracts',
                            'Global/NPC pose coverage and remaining art/effects/voices',
                            'Broader interruptions and background source/pause/load combinations']}
    (ROOT/'build/pride-game-over-latest.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Pride game-over milestone verified on current binaries; full first-level fidelity remains PARTIAL', flush=True)


if __name__ == '__main__': main()
