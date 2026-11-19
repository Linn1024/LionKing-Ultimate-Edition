"""Extend the frozen integration audit with actual320 completion and pose scope."""
import json
from pathlib import Path
import shutil

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    latest=ROOT/'build/pride-rng-player-latest.json'
    previous=ROOT/'build/pride-rng-player/integration-report.json'
    if not previous.exists():shutil.copy2(latest,previous)
    old=bound(previous);assert old['result']=='PARTIAL' and old['checks']==108
    base=ROOT/'build/pride-rng-player2';paths=[Path(__file__),previous];checks=old['checks']
    pose_path=base/'completion-pose-probe/report.json';pose=bound(pose_path)
    assert pose['result']=='PASS' and all(pose['checks'].values())
    assert pose['missing_poses']==[0x11372] and pose['pride_observations_of_missing']=={'0x11372':[]}
    checks+=len(pose['checks']);paths.append(pose_path)
    coverage_path=base/'pride-coverage/320/report.json';coverage=bound(coverage_path)
    assert coverage['result']=='PASS' and all(coverage['checks'].values())
    assert coverage['coverage_fields']==4419 and coverage['first_next_level_field']==4420
    checks+=len(coverage['checks']);paths.append(coverage_path)
    completed_path=base/'completion-reference-unpaused2/report.json';completed=bound(completed_path)
    missing={k for k,v in completed['checks'].items() if not v}
    assert completed['result']=='INCOMPLETE' and missing=={f'320/{m}/no_missing_observed_poses' for m in ('aot','lle')}
    assert completed['native_fields_compared']==6000
    assert completed['ordinary_poweron_controller_inputs_only'] and not completed['loaded_states'] and not completed['practice_or_guest_edits']
    checks+=sum(completed['checks'].values());paths.append(completed_path)
    narrow_path=base/'completion-reference-unpaused256/report.json';narrow=bound(narrow_path)
    narrow_missing={k for k,v in narrow['checks'].items() if not v}
    assert narrow['result']=='INCOMPLETE' and narrow_missing=={
        f'256/{m}/{k}' for m in ('aot','lle') for k in ('next_main_level','level_and_boss_music')}
    assert narrow['native_fields_compared']==6000
    paths.append(narrow_path)
    long_path=base/'completion-reference-long3/report.json';long=bound(long_path)
    assert long['result']=='INCOMPLETE' and {k for k,v in long['checks'].items() if not v}=={
        '320/aot/next_main_level','320/lle/next_main_level'}
    paths.append(long_path)
    for p in (base/'completion-reference-unpaused2/320/aot/window.png',):
        assert p.is_file();paths.append(p)
    report=dict(result='PARTIAL',checks=checks,
        preceding_compared_fields=old['compared_fields'],completion_compared_fields=6000,
        separate_boundary_replay_fields=4419,failed_256_route_compared_fields=6000,
        native_route_endpoints=75,native_allbugs_fields=60648,
        normal_rng_on_320_completion_verified=True,observed_pride_pose_coverage_verified=True,
        first_next_level_field=4420,next_level_native_fallback_poses=[0xc11372],
        normal_rng_on_256_completion_verified=False,full_first_level_fidelity_complete=False,
        public_player_enabled=False,public_preview_unchanged=True,
        retained_failed_checks_256=sorted(narrow_missing),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    retained=base/'integration-report2.json'
    assert not retained.exists()
    retained.write_text(json.dumps(report,indent=2)+'\n');shutil.copy2(retained,latest)
    print('PARTIAL',checks,'checks; ordinary320 completion verified;256 route/full fidelity open',flush=True)


if __name__=='__main__':main()
