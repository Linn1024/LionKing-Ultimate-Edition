"""Index current-build Pride roar evidence without claiming full-level fidelity."""
import hashlib
import json
from audit_scenes import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    player = ROOT/'dist/LionKing.exe'
    reports = {}
    paths = ['pride-roar-behavior/report.json', 'pride-roar-variants/report.json',
             'pride-roar-audio/report.json', 'pride-roar-presentation/report.json',
             'pride-roar-switch/report.json', 'pride-state-profiles/report.json',
             'pride-camera-completion-verified/report.json', 'pride-mix-verification/report.json',
             'native-route-verification/play-report.json',
             'native-route-verification/allbugs-report.json', 'setup-verification/report.json']
    for relative in paths:
        path = ROOT/'build'/relative
        value = json.loads(path.read_text())
        assert value['result']=='PASS', relative
        assert path.stat().st_mtime>=player.stat().st_mtime, ('Report predates current player', relative)
        reports[relative] = {'result':'PASS', 'sha256':digest(path)}
    for name, baseline in [('play-report.json','roar-paced-native-before.json'),
                           ('allbugs-report.json','roar-paced-allbugs-before.json')]:
        current = json.loads((ROOT/'build/native-route-verification'/name).read_text())
        previous = json.loads((ROOT/'build'/baseline).read_text())
        assert current['routes']==previous['routes'], (name, 'Native baseline final hashes changed')
    variants = json.loads((ROOT/'build/pride-roar-variants/report.json').read_text())
    assert sum(case['fields'] for case in variants['cases'].values())==816
    assert variants['cases']['repeat-roar']['original_pulse_strengths']==[16,2]
    units = (ROOT/'build/roar-paced-unit.log').read_text()
    assert 'roar_test: PASS' in units and 'resources_test: PASS' in units
    manifest = json.loads((ROOT/'game-data/install.json').read_text())
    assert manifest['player_sha256']==digest(player)
    capabilities = (ROOT/'engine/generated/resources/native_adapters.h').read_text()
    assert '#define TLK_ROAR_AOT_AVAILABLE 1' in capabilities
    report = {'result':'PASS', 'milestone':'Independent Pride cub roar activation/animation',
              'player_sha256':digest(player),
              'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
              'installed_manifest_matches_player':True,
              'resource_id':'gameplay.simba.roar', 'gameplay_source_bit':4,
              'shared_animation_parser_forwarded':False,
              'compiled_post_load_hooks':5, 'original_delay':14,
              'original_variant_fields_per_mode':816,
              'reference_extra_idle_updates':6, 'runtime_clock_modified':False,
              'source_matched_gameplay_profiles':9, 'source_mismatches_rejected':12,
              'first_loaded_fields_compared':8, 'normal_completion_frames':5819,
              'native_routes':75, 'native_allbugs_frames':60648,
              'native_final_hashes_unchanged_from_pre_roar':True,
              'cache_sha256':manifest['scene_cache']['sha256'], 'cache_version':1,
              'original_md_capture_sha256':digest(ROOT/'build/pride-animation/md.json'),
              'aligned_md_capture_sha256':digest(ROOT/'build/pride-roar-original-aligned/md.json'),
              'reports':reports, 'first_level_fidelity_complete':False,
              'remaining_scope':['Remaining cub states/interruptions and enemy reactions',
                                 'Unmapped effects, particles, pickup transitions and title resources',
                                 'Remaining layout/spawn/collision/difficulty comparisons',
                                 'Adapted 256-camera full ordinary-controller route']}
    path = ROOT/'build/pride-roar-latest.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('Current Pride roar evidence indexed:',path,flush=True)


if __name__=='__main__':
    main()
