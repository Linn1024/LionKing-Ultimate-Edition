"""Index verified final-level themes without claiming complete level adapters."""
import hashlib
import json
from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player = ROOT/'dist/LionKing.exe'
    reports = {}
    runtime = ('next-level-music/report.json', 'final-music-switch/report.json',
               'final-level-mix/report.json', 'next-level-launchers/report.json',
               'pride-audio-verification/report.json', 'setup-verification/report.json',
               'native-route-verification/play-report.json',
               'native-route-verification/allbugs-report.json')
    for name in (*runtime, 'final-music-reference/report.json'):
        path = ROOT/'build'/name
        row = json.loads(path.read_text())
        assert row['result'] == 'PASS', name
        if name in runtime:
            assert path.stat().st_mtime >= player.stat().st_mtime, ('Stale report', name)
        reports[name] = {'result': row['result'], 'sha256': digest(path)}
    music = json.loads((ROOT/'build/next-level-music/report.json').read_text())
    assert set(music['levels']) == {str(n) for n in range(1, 10)}
    mix = json.loads((ROOT/'build/final-level-mix/report.json').read_text())
    assert mix['frames'] == 60648 and mix['intermediate_hash_checks'] == 122
    assert {327, 311, 432} <= set(mix['required_md_programs'])
    native = json.loads((ROOT/'build/native-route-verification/play-report.json').read_text())
    assert native['route_count'] == 75
    manifest = json.loads((ROOT/'game-data/install.json').read_text())
    assert manifest['player_sha256'] == digest(player)
    report = {'result': 'PASS', 'milestone': 'Independent MD themes for all ten main levels',
              'player_sha256': digest(player),
              'headless_sha256': digest(ROOT/'engine/build-win/tlk_headless.exe'),
              'installed_manifest_matches_player': True,
              'new_programs': {'be_prepared': 327, 'simbas_return': 311, 'pride_rock': 432},
              'original_reference_frames': 55000, 'mixed_route_frames': 60648,
              'intermediate_hash_checks': 122, 'native_routes': 75,
              'verified_background_levels': manifest['scene_cache']['verified_background_levels'],
              'cache_sha256': manifest['scene_cache']['sha256'], 'reports': reports,
              'full_levels_complete': False,
              'remaining': ['Later-level background, sprite, gameplay and effect adapters',
                            'Later death, victory and other music events',
                            'MD audio playback continuation across saves',
                            'Remaining Pride Lands fidelity checklist']}
    out = ROOT/'build/final-music-latest.json'
    out.write_text(json.dumps(report, indent=2)+'\n')
    print('Final-level music evidence indexed:', out, flush=True)


if __name__ == '__main__':
    main()
