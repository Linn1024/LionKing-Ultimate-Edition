"""Index next-level cub artwork and retained gates without claiming complete levels."""
import hashlib
import json
from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player = ROOT/'dist/LionKing.exe'
    reports = {}
    runtime = ('next-cub-art/report.json', 'next-cub-switch/report.json',
               'next-level-mix/report.json', 'next-level-music/report.json',
               'next-level-launchers/report.json', 'pride-mix-verification/report.json',
               'pride-presentation-state/report.json', 'setup-verification/report.json',
               'native-route-verification/play-report.json', 'native-route-verification/allbugs-report.json')
    for name in (*runtime, 'next-cub-reference/report.json'):
        path = ROOT/'build'/name
        row = json.loads(path.read_text())
        assert row['result'] == 'PASS', name
        if name in runtime:
            assert path.stat().st_mtime >= player.stat().st_mtime, ('Stale report', name)
        reports[name] = {'sha256': digest(path), 'result': row['result']}
    art = json.loads((ROOT/'build/next-cub-art/report.json').read_text())
    if not art.get('unsupported_adult_window_and_guest_unchanged'):
        path = ROOT/'build/next-cub-art/adult-report.json'
        adult = json.loads(path.read_text())
        assert adult['result'] == 'PASS' and adult['unsupported_adult_window_and_guest_unchanged']
        assert path.stat().st_mtime >= player.stat().st_mtime
        reports['next-cub-art/adult-report.json'] = {'sha256': digest(path), 'result': 'PASS'}
    gap_path = ROOT/'build/cant-wait-background/report.json'
    gap = json.loads(gap_path.read_text())
    assert gap['result'] == 'TIMING_VERIFIED_PENDING_ADAPTER' and not gap['background_enabled']
    reports['cant-wait-background/report.json'] = {'sha256': digest(gap_path), 'result': gap['result']}
    for name, before in (('play-report.json', 'lizard-defeat-native-before.json'),
                         ('allbugs-report.json', 'lizard-defeat-allbugs-before.json')):
        current = json.loads((ROOT/'build/native-route-verification'/name).read_text())
        previous = json.loads((ROOT/'build'/before).read_text())
        assert current['routes'] == previous['routes'], 'Native baseline changed'
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes() == (ROOT/'build/hyena-taunt-allbugs-before.ram').read_bytes()
    manifest = json.loads((ROOT/'game-data/install.json').read_text())
    assert manifest['player_sha256'] == digest(player)
    assert manifest['scene_cache']['version'] == 1 and manifest['scene_cache']['verified_background_levels'] == [0, 2]
    report = {'result': 'PASS', 'scope': __doc__, 'resource_id': 'graphics.sprites.simba.cub.frames',
              'new_scene_descriptors': {'1': '03b9', '2': '03eb'},
              'player_sha256': digest(player), 'headless_sha256': digest(ROOT/'engine/build-win/tlk_headless.exe'),
              'installed_manifest_matches_player': True, 'cache': manifest['scene_cache'],
              'observed_mapped_cub_poses': {level: row['runs']['frames']['coverage']['seen_by_role']['cub']
                                          for level, row in art['levels'].items()},
              'observed_native_fallback_poses': {level: row['runs']['frames']['coverage']['missing_poses']
                                               for level, row in art['levels'].items()},
              'live_switch_without_restart': True, 'native_baselines_unchanged': True,
              'native_routes': 75, 'tracked_native_allbugs_fields': 60648,
              'reports': reports, 'full_later_level_fidelity_complete': False,
              'remaining': ['Second-level native ostrich offset and scenery palette correspondence, renderer and transitions',
                            'Later enemy/ride sprites, unknown cub poses and independent original action timing',
                            'Other scene layers/effects, gameplay/layout/collision and interruption paths',
                            'Full Pride checklist remains open']}
    path = ROOT/'build/next-cub-latest.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print('Next-level cub artwork and retained baseline evidence indexed:', path, flush=True)


if __name__ == '__main__':
    main()
