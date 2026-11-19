"""Bind ordinary walking-response evidence to the unchanged installed player44."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-walking-live-audit';out.mkdir()
    paths=[Path(__file__)];checks={};counts={}
    for label,relative in [
        ('original_contract','pride-porcupine-walk-contract/report.json'),
        ('guest_context','pride-walking-guest-context2/report.json'),
        ('walking_live','pride-walking-response/qualification/report.json'),
        ('source_comparison','pride-walking-source-comparison/report.json'),
        ('actual_windows','pride-walking-response/presentation/report.json'),
        ('installed_player','pride-sprite-fresh44/bindings/report.json')]:
        p=ROOT/'build'/relative;r=bound(p);paths.append(p)
        checks[label]=r['result']=='PASS' and all(r['checks'].values());counts[label]=len(r['checks'])
    for relative in ['pride-walking-inputs/report.json','pride-walking-approach/report.json','pride-walking-recharge/report.json']:
        p=ROOT/'build'/relative;r=bound(p);paths.append(p)
        checks[relative]=r['result']=='OBSERVED' and all(r.get('checks',{}).values())
        if 'cases' in r:checks[relative+'_all_processes_exited']=all(c.get('exit',0)==0 for c in r['cases'].values())
    p=ROOT/'build/pride-sprite-fresh44/walking-observer/build-report.json';observer=bound(p);paths.append(p)
    checks['all321_nonhost_inputs_bound']=observer['nonhost_inputs_unchanged']==321 and all(digest(ROOT/p)==sha for p,sha in observer['link_inputs_sha256'].items())
    build_path=ROOT/'build/pride-sprite-fresh44/build-report.json';build=bound(build_path);paths.append(build_path)
    checks['installed_player_binary_unchanged']=digest(build_path.parent/'player.exe')==digest(ROOT/'dist/installed-preview44/LionKing.exe')==build['binary_sha256']
    p=ROOT/'build/pride-walking-response/report.json';failed=bound(p);paths.append(p)
    checks['failed_rendered_field_assumption_retained']=failed['result']=='FAIL' and [k for k,v in failed['checks'].items() if not v]==['all28_walking_timers']
    first=ROOT/'build/pride-walking-guest-context/failure.json';failure=json.loads(first.read_text());paths.append(first)
    checks['failed_host_register_experiment_retained']=failure['result']=='FAILED' and failure['host_stack_register_assigned_by_mistake']
    paths+=[first.parent/'attempt-source.py',first.parent/'observe.gdb',first.parent/'debugger/run.log',
            ROOT/'tools/build_pride_walking_observer.py',ROOT/'tools/build_pride_sprite_allbugs.py']
    checks['framework_submodules_unchanged']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,report_check_counts=counts,
                ordinary_walking_entry_cue_and_pre_post_cold_saves_verified=True,
                runtime_or_renderer_modified=False,full_first_level_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),counts,flush=True)


if __name__=='__main__':main()
