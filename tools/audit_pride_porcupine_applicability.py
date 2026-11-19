"""Bind terrain-driven choice applicability and ordinary active attack coverage."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-applicability';out.mkdir()
    checks={};counts={};reports={};paths=[Path(__file__)]
    for label,relative,count in [
        ('selectors','pride-nonpersistent-selector/report.json',1030),
        ('original_choices','pride-porcupine-choice-originals/report.json',11268),
        ('ordinary_lifetimes','pride-porcupine-lifetimes/report.json',56),
        ('actual_facing_windows','pride-porcupine-facing-windows/report.json',14),
        ('adapted_branch_matrix','pride-porcupine-component/report.json',708),
        ('previous_walking','pride-walking-live-audit/report.json',17),
        ('installed44','pride-sprite-fresh44/bindings/report.json',20)]:
        p=ROOT/'build'/relative;r=bound(p);paths.append(p);reports[label]=r
        checks[label]=r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values());counts[label]=len(r['checks'])
    choice=reports['original_choices']
    checks['synthetic_attack_controls_not_authored']=not set(choice['synthetic_control_attributes'])&set(choice['authored_attributes'])
    checks['ordinary_mixed_attacks_both_facings']=all(reports['ordinary_lifetimes']['cases'][label]['attack_facings']==[0,1] for label in ('mixed-aot','mixed-lle'))
    checks['ordinary_native_coverage_not_overstated']=all(reports['ordinary_lifetimes']['cases'][label]['attack_facings']==[1] for label in ('native-aot','native-lle'))
    failure_path=ROOT/'build/pride-porcupine-lifetimes/failure.json';failure=json.loads(failure_path.read_text());paths.append(failure_path)
    runner=ROOT/'tools/verify_pride_porcupine_lifetimes.py';paths.append(runner)
    checks['failed_native_trace_assumption_preserved']=failure['result']=='FAILED' and failure['runner_sha256']==digest(runner)==digest(failure_path.parent/'attempt-source.py')
    checks['all_five_player_runs_succeeded']=len(failure['player_returns'])==5 and set(failure['player_returns'].values())=={0}
    build_path=ROOT/'build/pride-sprite-fresh44/build-report.json';build=bound(build_path);paths.append(build_path)
    checks['production_binary_and_all322_inputs_unchanged']=digest(build_path.parent/'player.exe')==digest(ROOT/'dist/installed-preview44/LionKing.exe')==build['binary_sha256'] and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    observer_path=ROOT/'build/pride-sprite-fresh44/porcupine-lifetime-observer/build-report.json';observer=bound(observer_path);paths.append(observer_path)
    checks['all321_nonhost_inputs_unchanged']=observer['nonhost_inputs_unchanged']==321 and all(digest(ROOT/p)==sha for p,sha in observer['link_inputs_sha256'].items())
    checks['framework_submodules_unchanged']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths += [ROOT/'tools/build_pride_porcupine_lifetime_observer.py',ROOT/'tools/build_pride_sprite_allbugs.py',
              ROOT/'tools/qualify_pride_porcupine_lifetimes.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,report_check_counts=counts,
                authored_pride_terrain_does_not_select_nonpersistent_attack=True,
                synthetic_nonpersistent_adapter_behavior_retained=True,
                complete_dynamic_unreachability_or_whole_enemy_equivalence_claimed=False,
                first_level_complete=False,runtime_or_renderer_changed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),counts,flush=True)


if __name__=='__main__':main()
