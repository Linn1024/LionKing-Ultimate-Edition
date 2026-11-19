"""Index the current player's later-music verification and retained limitations."""
import hashlib
import json
from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player = ROOT/'dist/LionKing.exe'
    player_hash = digest(player)
    reports = {}
    paths = ['next-level-music/report.json', 'stampede-music-switch/report.json',
             'later-level-mix/report.json', 'next-level-launchers/report.json',
             'pride-audio-verification/report.json', 'setup-verification/report.json',
             'native-route-verification/play-report.json',
             'native-route-verification/allbugs-report.json']
    for relative in paths + ['later-music-reference/report.json']:
        path = ROOT/'build'/relative
        row = json.loads(path.read_text())
        assert row['result'] == 'PASS', relative
        if relative in paths:
            assert path.stat().st_mtime >= player.stat().st_mtime, ('Report predates player', relative)
        reports[relative] = {'result': row['result'], 'sha256': digest(path)}
    manifest = json.loads((ROOT/'game-data/install.json').read_text())
    assert manifest['player_sha256'] == player_hash, 'Refresh installed manifest with Setup.cmd'
    mix = json.loads((ROOT/'build/later-level-mix/report.json').read_text())
    assert mix['frames'] == 40000 and mix['intermediate_hash_checks'] == 80
    routes = json.loads((ROOT/'build/native-route-verification/play-report.json').read_text())
    assert routes['route_count'] == 75
    report = {'result':'PASS', 'milestone':'Independent MD level music through Simba Destiny',
              'player_sha256':player_hash,
              'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
              'installed_manifest_matches_player':True,
              'verified_background_levels':manifest['scene_cache']['verified_background_levels'],
              'cache_sha256':manifest['scene_cache']['sha256'],
              'new_music_programs':{'stampede':145, 'simbas_exile':258,
                                    'hakuna_matata':40, 'simbas_destiny':281},
              'original_music_evidence':'Unmodified matching BizHawk 2.11 movie, 40000 frames',
              'standalone_md_research_core_later_sync':False,
              'normal_controller_mix_frames':40000, 'intermediate_hash_checks':80,
              'native_routes':75, 'native_allbugs_frames':60648,
              'reports':reports,
              'remaining':['Per-scene later background/sprite/gameplay adapters',
                           'Later death/victory/effect music events',
                           'Remaining Pride source-fidelity checklist'],
              'roar_prototype_shipped':False}
    path = ROOT/'build/later-music-latest.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print('Later-level music evidence indexed:', path, flush=True)


if __name__ == '__main__':
    main()
