"""Bind the checkpoint player adapter and regressions; full Pride remains open."""
import hashlib
import argparse
import json
from pathlib import Path

from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interaction',action='store_true')
    args=parser.parse_args()
    generation=3 if args.interaction else 2
    output = ROOT/'build/pride-checkpoint-player'
    player = digest(ROOT/'engine/build-win/tlk_sdl.exe')
    headless = digest(ROOT/'engine/build-win/tlk_headless.exe')
    assert digest(ROOT/'dist/LionKing.exe') == player
    assert digest(output/'baseline-sdl.exe') == 'd49a9374c73795e5885e7e0e7f0977bd172222e5c8a813e3006982c51719788b'
    assert digest(output/'baseline-headless.exe') == '9a1c5953d571b889ae55bd54477c8cc458856f84f44f95aae9b0144a5c664af6'
    evidence = {}

    def load(key, relative,expected_result='PASS'):
        path = ROOT/relative
        report = json.loads(path.read_text())
        assert report['result'] == expected_result, (key, report.get('result'))
        evidence[key] = dict(path=relative,sha256=digest(path))
        return path,report

    def sources(report):
        for name,sha in report.get('source_sha256',{}).items():
            assert digest(ROOT/name) == sha,name

    def artifacts(folder, report):
        for name,sha in report['artifacts_sha256'].items():
            assert digest(folder/name) == sha,(folder,name)

    path,identity = load('checkpoint_identity','build/pride-checkpoint-art/report.json')
    sources(identity);artifacts(path.parent,identity)
    assert identity['ordinary_collectible_c5889a_copied_ram_cases'] == (26 if args.interaction else 23)
    assert identity['copied_ram_cases'] == (366 if args.interaction else 357) and identity['relocated_task_and_draw_fixtures'] == 2
    if args.interaction:
        assert identity['ordinary_interaction_pose_copied_ram_cases'] == 3
    path,art = load('checkpoint_art','build/pride-checkpoint-art/art-report.json')
    sources(art);artifacts(path.parent,art)
    assert art['independent_frame_palette_combinations'] == 4 and art['source_detached']
    if args.interaction:
        assert art['checkpoint_image_count'] == 3 and art['interaction_source_indexed_pixels'] == 3840
        assert art['interaction_sampled_colors'] == 7680
        path,original_md=load('original_md_interaction',
            'build/pride-checkpoint-player/original-md-interaction/report.json','AUDITED')
        sources(original_md);artifacts(path.parent,original_md)
        assert original_md['ordinary_power_on'] and not original_md['guest_or_rom_edits']
        assert set(map(int,original_md['original_pose_values_observed'])) == {0x973b6,0x977c6,0x977fe}
        assert not original_md['cross_version_animation_timing_equivalence_verified']
        path,md_display=load('original_md_interaction_display',
            'build/pride-checkpoint-player/original-md-display/report.json')
        sources(md_display);artifacts(path.parent,md_display)
        assert md_display['ordinary_power_on'] and not md_display['guest_edits'] and not md_display['loaded_states']
        assert md_display['captured_fields'] == 101 and md_display['matched_fields'] == 89
        assert md_display['texture_indices'] == 89024 and md_display['original_palette_bank0_verified']
        assert all(md_display['pose_matched_fields'][str(p)] for p in (0x973b6,0x977c6,0x977fe))
        assert not md_display['final_window_or_cross_version_timing_verified']
    interaction_path = output/'interaction-audit/report.json'
    interaction = json.loads(interaction_path.read_text())
    assert interaction['result'] == 'AUDITED'
    sources(interaction)
    assert interaction['production_static_head_only'] and not interaction['interaction_poses_adapted']
    assert not interaction['original_md_usage_or_timing_verified']
    assert not interaction['physical_oam_or_final_pixels_verified']
    assert len(interaction['source_pairs']) == 2
    for pair in interaction['source_pairs']:
        bitmap = interaction_path.parent/f"{pair['snes_pose'] & 0x3fffff:06x}-indexed.bin"
        assert digest(bitmap) == pair['bitmap_sha256']
    evidence['interaction_inventory'] = dict(path=str(interaction_path.relative_to(ROOT)).replace('\\','/'),
                                            sha256=digest(interaction_path))
    window_cases = head_pixels = full_window_pixels = 0
    frames=[(5400,18),(3685,4)]
    if args.interaction:
        frames += [(3657,16),(3662,16)]
    for frame,count in frames:
        path,report = load(f'windows-{frame}',f'build/pride-checkpoint-player/windows-{frame}/report.json')
        assert report['candidate_sha256'] == player and len(report['cases']) == count
        assert report['ordinary_inputs'] and not report['practice_or_guest_edits']
        if frame in (3657,3662):
            assert report['full_matrix'] and report['pose'] == {3657:0xc2fde1,3662:0xc2fe18}[frame]
        sources(report)
        for case,result in report['cases'].items():
            folder = path.parent/case
            capture = json.loads((folder/'capture.json').read_text())
            assert capture['execution_completed'] and capture['binary_sha256'] == player
            assert capture['profile_sha256'] == digest(folder/'resources.ini')
            sources(capture);artifacts(folder,result)
            assert result['guest_and_native_pcm_exact']
            width = int(case.split('-')[0])
            expected_pixels={3657:473,3662:535}.get(frame,623 if frame == 3685 and width == 256 else 657)
            assert result['original_head_pixels'] == expected_pixels
            head_pixels += result['original_head_pixels']*4
            if result['full_window_matches_original_head_only_change']:
                full_window_pixels += width*2*448
            else:
                assert result['checkpoint_stays_native_with_md_siblings']
            window_cases += 1
    path,state = load('state','build/pride-checkpoint-player/state/report.json')
    sources(state)
    assert state['candidate_sha256'] == player and len(state['cases']) == 17 and state['previous_shipped_save_exact']
    for case,result in state['cases'].items():
        assert result['cross_source_window_and_guest_exact'] and result['complete_pcm_tail_exact']
        artifacts(path.parent/case,result)
    path,switch = load('live_switch','build/pride-checkpoint-player/switch/report.json')
    sources(switch);artifacts(path.parent,switch)
    assert switch['candidate_sha256'] == player and switch['actual_F12_inheritance_and_live_overrides']
    assert switch['level_not_restarted'] and switch['original_head_pixels_verified'] == 17739
    path,fallback = load('fallback_ui','build/pride-checkpoint-player/fallback-ui/report.json')
    sources(fallback);artifacts(path.parent,fallback)
    assert fallback['candidate_sha256'] == player and fallback['only_checkpoint_active_labels_changed']
    assert fallback['diagnostic_practice_scene_only'] and fallback['guest_hashes_exact']
    _,native = load('native75',f'build/pride-checkpoint-player/native{generation}/play-report.json')
    _,bugs = load('allbugs',f'build/pride-checkpoint-player/native{generation}/allbugs-report.json')
    for report in (native,bugs):
        assert report['binary_sha256'] == headless
        assert report['verifier_sha256'] == digest(ROOT/'tools/verify_native_routes.py')
    assert native['route_count'] == 75 and bugs['allbugs_tracked_ram_equal_every_frame']
    old_native = json.loads((ROOT/'build/native-route-verification/play-report.json').read_text())
    old_bugs = json.loads((ROOT/'build/native-route-verification/allbugs-report.json').read_text())
    assert native['routes'] == old_native['routes'] and bugs['routes'] == old_bugs['routes']
    current_ram = ROOT/f'build/pride-checkpoint-player/native{generation}/allbugs-aot.ram'
    assert current_ram.read_bytes() == current_ram.with_name('allbugs-lle.ram').read_bytes()
    assert current_ram.read_bytes() == (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes()
    for scenario in ('gameplay','gameplay256','media','media256'):
        path,report = load(scenario,f'build/pride-checkpoint-player/completion{generation}/{scenario}/report.json')
        assert report['checkpoint_sources'] and report['normal_first_level_completion_verified']
        assert not report['loaded_states'] and not report['actor_or_world_edits']
        assert report['executed_host_sha256'] == (player if report['media'] else headless)
        assert report['verifier_sha256'] == digest(ROOT/'tools/verify_pride_authored_route.py')
        old = json.loads((ROOT/f'build/pride-authored-completion/{scenario}/report.json').read_text())
        assert report['execution_modes'] == old['execution_modes']
        if report['media']:
            assert report['exact_mixed_wav_sha256'] == old['exact_mixed_wav_sha256']
    _,windows = load('generic_windows','build/windows-smoke/report.json')
    assert windows['live_F10_round_trip'] and windows['unadapted_background_native_fallback']
    _,setup = load('installer','build/setup-verification/report.json')
    assert setup['actual_setup_window'] and setup['source_roms_settings_and_saves_unchanged']
    _,launchers = load('installed_launchers','build/next-level-launchers/report.json')
    assert len(launchers['levels']) == 9
    post_identity = json.loads((output/'post-gates.json').read_text())
    assert post_identity['result'] == 'PASS' and post_identity['player_sha256'] == player
    if args.interaction:
        assert post_identity['interaction_image_matrices_required'] and post_identity['evidence_generation'] == 3
    assert 'remap_selftest: PASS (0 failed)' in (output/'remap.log').read_text(errors='replace')
    for name,sha in post_identity['reports_sha256'].items():
        assert digest(ROOT/name) == sha,name
    result = dict(result='PARTIAL',scope=__doc__,production_sha256={'dist/LionKing.exe':player,
        'engine/build-win/tlk_headless.exe':headless},checkpoint_renderer_integrated=True,
        checkpoint_static_head_independent_frames_and_palettes=True,ordinary_window_cases=window_cases,
        checkpoint_interaction_blink_artwork_adapted=args.interaction,
        original_md_interaction_timing_equivalence_verified=False,
        original_md_interaction_uploaded_sprite_data_verified=args.interaction,
        independently_verified_head_client_pixels=head_pixels,complete_window_pixels_compared=full_window_pixels,
        actual_F12_live_overrides=True,cross_process_source_cases=17,previous_shipped_save_exact=True,
        off_pride_native_fallback_labels_verified=True,
        native_routes=75,allbugs_fields=60648,healthy_completion_cases=8,
        evidence=evidence,source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))},
        full_first_level_fidelity_complete=False,production_death_behavior_enabled=False,
        remaining=([ 'Compare original checkpoint interaction timing, active SAT and transition-field source handling' ] if args.interaction else [
            'Adapt checkpoint interaction images C2FDE1/C2FE18 with independent sources; current head adapter covers the base image only'])+[
            'Integrate selectable death/revival scene ownership with correct HUD/object/source/layout semantics',
            'Verify compiled scene ownership, input boundaries, default/final-life contexts and source audio phase/policy',
            'Complete scene lifecycle, active saves, pause/reset/source switching for the new death behavior',
            'Audit the complete Pride Lands fidelity checklist before starting the authorized remaining-levels goal'
        ])
    (ROOT/'build/pride-checkpoint-player-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Checkpoint player source/UI/state/window and fresh production gates verified; full Pride remains PARTIAL',flush=True)


if __name__ == '__main__':
    main()
