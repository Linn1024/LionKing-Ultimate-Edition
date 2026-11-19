"""Bind verified launch-audio scopes while keeping full Pride fidelity open."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player';destination=base/'launch-integration-report.json'
    assert not destination.exists(),'Preserve frozen successful summaries'
    bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    expected={'launch-audio-baselines':78,'launch-saves':120,'launch-pause':8,
        'launch-changed-source':20,'previous-native-save':10,'launch-restart':12,
        'regression':20,'width-completion':21,'launch-route':19,
        'allbugs-standalone':10,'launch-music-mix':34}
    paths=[Path(__file__),bp,ROOT/'tools/pride_lizard_launch_history.py'];count=0
    for name,number in expected.items():
        p=base/name/'report.json';r=bound(p)
        assert r['result']=='PASS' and len(r['checks'])==number and all(r['checks'].values()),p
        count+=number;paths.append(p)
    gates=base/'native-gates/play-report.json';native=json.loads(gates.read_text())
    reference=ROOT/'build/pride-reset/fixed4/native/gates/play-report.json'
    assert native['result']=='PASS' and native['route_count']==75
    assert native['binary_sha256']==build['binary_sha256']
    assert native['routes']==json.loads(reference.read_text())['routes']
    paths.extend((gates,reference))
    for name,result in (
        ('build/pride-lizard-launch-audio/report.json','ORIGINAL_LIZARD_LAUNCH_SOUND_DIFFERENCE_VERIFIED'),
        ('build/pride-lizard-launch-work/component/report.json','PASS'),
        ('build/pride-lizard-launch-tail/report.json','PASS'),
        ('build/pride-lizard-launch-driver-parameter/report.json','CONTROLLED_FM123_PARAMETERS_PCM_IDENTICAL'),
        ('build/pride-lizard-launch-work/exit-mx-comparison.json','UNCHANGED_UNPROVEN_BASELINE')):
        p=ROOT/name;assert bound(p)['result']==result;paths.append(p)
    remap=base/'remap/run.log';assert 'PASS (0 failed)' in remap.read_text()
    tests=ROOT/'build/pride-lizard-launch-work/python-tests.log';raw=tests.read_bytes()
    assert '23 passed, 4 skipped' in raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8-sig')
    paths.extend((remap,tests))
    assert count==352
    report=dict(result='PARTIAL',checks=count,binary_sha256=build['binary_sha256'],
        native75_endpoint_pairs=75,native_allbugs_tracked_fields_per_mode=60648,
        cold_load_mode_combinations=24,cold_prefix_repeated_fields=28330,cold_remaining_repeated_fields=51340,
        changed_source_load_combinations=4,previous_build_native_load_modes=2,
        audible_original_launches_per_route=2,cue_using_music_mix_verified=True,
        narrow_supported_mixture_launches=0,narrow_mixture_does_not_prove_launch_cue_coverage=True,
        static_wrong=0,static_unproven=11,complete_static_proof=False,
        existing_bounce_timing_equivalence_proven=False,
        preview_promoted=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL352: launch-audio integration; full Pride fidelity remains open',flush=True)


if __name__=='__main__':main()
