"""Index verified Exile artwork and second-level timing without claiming full levels."""
import hashlib
import json
from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player = ROOT/'dist/LionKing.exe'
    reports = {}
    names = ('exile-cub-art/report.json', 'exile-cub-switch/report.json',
             'later-level-mix/report.json', 'next-level-launchers/report.json',
             'setup-verification/report.json',
             'native-route-verification/play-report.json', 'native-route-verification/allbugs-report.json')
    for name in (*names, 'exile-cub-reference/report.json', 'cant-wait-timing/report.json'):
        path = ROOT/'build'/name
        row = json.loads(path.read_text())
        assert row['result'] == 'PASS', name
        if name in names:
            assert path.stat().st_mtime >= player.stat().st_mtime, ('Stale runtime report', name)
        reports[name] = {'sha256': digest(path), 'result': row['result']}
    for name, before in (('play-report.json', 'pride-activation-native-before.json'),
                         ('allbugs-report.json', 'pride-activation-allbugs-before.json')):
        assert json.loads((ROOT/'build/native-route-verification'/name).read_text())['routes'] == json.loads((ROOT/'build'/before).read_text())['routes']
    assert (ROOT/'build/native-route-verification/allbugs-aot.ram').read_bytes() == (ROOT/'build/pride-activation-allbugs-before.ram').read_bytes()
    manifest = json.loads((ROOT/'game-data/install.json').read_text())
    assert manifest['player_sha256'] == digest(player)
    assert manifest['scene_cache']['verified_background_levels'] == [0, 2]
    art = json.loads((ROOT/'build/exile-cub-art/report.json').read_text())['levels']['4']
    timing = json.loads((ROOT/'build/cant-wait-timing/report.json').read_text())
    report = {'result': 'PASS', 'scope': __doc__, 'player_sha256': digest(player),
              'headless_sha256': digest(ROOT/'engine/build-win/tlk_headless.exe'),
              'resource_id': 'graphics.sprites.simba.cub.frames', 'new_descriptor': '4/044f',
              'observed_mapped_poses': art['runs']['frames']['coverage']['seen_by_role']['cub'],
              'observed_native_fallback_poses': art['runs']['frames']['coverage']['missing_poses'],
              'native_routes_unchanged': 75, 'tracked_allbugs_fields_unchanged': 60648,
              'second_level_original_visible_scroll_fields': timing['matched_vdp_fields'],
              'verified_background_levels': [0, 2], 'installed_manifest_matches_player': True,
              'reports': reports, 'full_later_level_fidelity_complete': False,
              'remaining': ['Second-level native ostrich offset and palette mapping, renderer and transitions',
                            'Other later-level enemies, scenery/effects, timing and gameplay/layout differences',
                            'Exile continuation descriptor and additional cub poses',
                            'Pride full fidelity and MD-camera completion regression remain open']}
    path = ROOT/'build/exile-cub-latest.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print('Exile artwork, second-level timing and retained native gates indexed:', path, flush=True)


if __name__ == '__main__':
    main()
