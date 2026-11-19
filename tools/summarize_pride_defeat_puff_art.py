"""Index independent puff art and retained first-level gates; full Pride remains open."""
import hashlib
import json
import re
from collections import Counter
from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player = ROOT/'dist/LionKing.exe'
    runtime = ('pride-defeat-puff-art/report.json', 'pride-defeat-puff-switch/report.json',
               'pride-npc-verification/report.json', 'pride-state-verification/report.json',
               'pride-leaf-verification/report.json', 'pride-mix-verification/report.json',
               'pride-camera-completion-verified/report.json', 'pride-lizard-defeat/report.json',
               'pride-presentation-state/report.json', 'presentation-schema-compat/report.json',
               'pride-audio-state/report.json', 'setup-verification/report.json',
               'native-route-verification/play-report.json', 'native-route-verification/allbugs-report.json',
               'next-cub-art/adult-report.json', 'next-level-mix/report.json')
    reports = {}
    for name in (*runtime, 'defeat-puff-art/report.json', 'lizard-defeat-original/native.json',
                 'lizard-defeat-original/md.json', 'lizard-defeat-original/comparison.json'):
        path = ROOT/'build'/name
        row = json.loads(path.read_text())
        assert row['result'] == 'PASS', name
        if name in runtime:
            assert path.stat().st_mtime >= player.stat().st_mtime, ('Stale report', name)
        reports[name] = {'result': 'PASS', 'sha256': digest(path)}
    for name, previous in (('play-report.json', 'defeat-puff-native-before.json'),
                           ('allbugs-report.json', 'defeat-puff-allbugs-before.json')):
        a = json.loads((ROOT/'build/native-route-verification'/name).read_text())
        b = json.loads((ROOT/'build'/previous).read_text())
        assert a['routes'] == b['routes'], 'Native final hashes changed'
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes() == (ROOT/'build/defeat-puff-allbugs-before.ram').read_bytes()
    manifest = json.loads((ROOT/'game-data/install.json').read_text())
    assert manifest['player_sha256'] == digest(player)
    cache = manifest['scene_cache']
    assert cache['version'] == 1 and cache['verified_background_levels'] == [0, 2]
    assert cache['sha256'] == '94e6d05bad469ca7767ddd0878e2a5b057f379f99736744f471f89598d3c94d6'
    raw = (ROOT/'build/defeat-puff-art-mx.log').read_bytes()
    log = raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
    wrong = len(re.findall(r'^WRONG\b', log, re.M))
    unproven = len(re.findall(r'^UNPROVEN\b', log, re.M))
    assert wrong == 0 and unproven == 11
    counts = Counter(r['role'] for r in json.loads((ROOT/'tools/pride_npc_pairs.json').read_text())['pairs'])
    assert counts['defeat_puff'] == 8 and counts['porcupine'] == 15
    art = json.loads((ROOT/'build/pride-defeat-puff-art/report.json').read_text())
    assert len(art['original_phases']) == 8 and art['controlled_unreviewed_palette_bank_retains_native_window']
    original_art = json.loads((ROOT/'build/defeat-puff-art/report.json').read_text())
    assert len(original_art['pairs']) == 8 and original_art['live_md_palette_checks'] == 64
    assert all(p['mask_difference'] == p['indexed_difference'] == 0 and
               p['native_origin_size'] == p['md_origin_size'] for p in original_art['pairs'])
    report = {'result': 'PASS', 'scope': __doc__, 'resource_id': art['source_id'],
              'player_sha256': digest(player), 'headless_sha256': digest(ROOT/'engine/build-win/tlk_headless.exe'),
              'installed_manifest_matches_player': True, 'scene_cache': cache,
              'catalog_roles': dict(counts), 'newly_separate_effect_poses': 8,
              'newly_discovered_art_images': 0, 'all_eight_original_indexed_images_identical': True,
              'paired_original_timer_phase_updates': 64, 'live_original_md_palette_checks': 64,
              'native_live_draw_palette_and_cgram_verified': True,
              'source_independence_and_live_f12_inheritance_verified': True,
              'first_loaded_art_fields': art['first_loaded_fields'], 'native_baselines_unchanged': True,
              'native_routes': 75, 'tracked_allbugs_fields': 60648,
              'exit_mx': {'wrong': wrong, 'existing_unproven': unproven, 'full_proof': False},
              'reports': reports, 'full_first_level_fidelity_complete': False,
              'remaining': ['Other particles/pickup transitions/title resources and exceptional effect uses',
                            'Other cub/enemy states and original timing, damage/death/revival and interruptions',
                            'Active effect lifetime/removal evidence beyond retained actor memory',
                            'Enemy reactions/spawn/layout/collision/difficulty and remaining audio semantics',
                            'Adapted256 ordinary completion and the full Pride checklist']}
    path = ROOT/'build/pride-defeat-puff-art-latest.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print('Independent shared puff art and retained Pride baselines indexed:', path, flush=True)


if __name__ == '__main__':
    main()
