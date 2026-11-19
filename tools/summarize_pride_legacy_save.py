"""Bind genuine installed saves, actionable rejection and current-format replay."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-legacy-save';paths=[Path(__file__)];reports={};passed=0;checks={}
    def read(path,result='PASS'):
        nonlocal passed
        r=bound(path);assert r['result']==result,(path,r['result'])
        if result=='PASS':assert all(r['checks'].values()),path;passed+=len(r['checks'])
        paths.append(path);reports[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path);return r
    prior=read(ROOT/'build/pride-tree-help-latest.json','PARTIAL');assert prior['checks_passed']==88
    build=read(base/'player/build-report.json','BUILT');probe=read(base/'probe/report.json','OBSERVED')
    for case in ('native','md-media'):
        row=probe['observations'][case]
        checks[case+'/genuine_installed_v7_save']=row['outer_version']==4 and row['saved_field']==1500 and row['runtime_markers']==[[297411,7]] and row['loads']['installed']['exit']==0
        checks[case+'/reproduced_candidate_incompatibility']=row['loads']['native']['exit']==8 and row['loads']['mixed']['exit']==8
    for name,folder in (('mixed',ROOT/'build/pride-tree-help2'),('native',ROOT/'build/pride-tree-help2/plain-native')):
        old=read(folder/'build-report.json','BUILT');value=build['runs'][name];assert digest(base/'player'/(name+'.exe'))==value['binary_sha256']
        for file,sha in value['production_sha256'].items():assert digest(ROOT/file)==sha,file
        for file,sha in value['link_inputs_sha256'].items():assert digest(ROOT/file)==sha,file
        a,b=old['link_inputs_sha256'],value['link_inputs_sha256'];shared=set(a)&set(b)
        checks[name+'/unchanged_core_objects']=all(a[k]==b[k] for k in shared)
        count=2 if name=='mixed' else 1
        checks[name+'/only_save_io_and_private_guard_changed']=len(set(a)-set(b))==len(set(b)-set(a))==count
    pixels=0
    for case in ('native','mixed-native','mixed-md'):
        r=read(base/'verified'/case/'report.json');host='mixed' if case!='native' else 'native';assert r['binary_sha256']==build['runs'][host]['binary_sha256']
        pixels+=(640 if case=='mixed-md' else 512)*448
    replay=read(base/'current-format2/report.json')
    # The initial cross-private-build replay is intentionally not relabelled.
    # Its checksum-bound executable ID differs; each passing control authors
    # its own identity instead of rewriting that identity in the save.
    raw=base/'current-format/mixed-native/run.log';paths.append(raw)
    checks['preserved_cross_private_build_rejection']='Save is incompatible or damaged' in raw.read_text()
    bank=ROOT/'tools/pride_repeat_bank.c';paths.append(bank)
    checks['private_executable_identity_limitation_recorded']='sha256_compute(bytes,(size_t)size,build_digest)' in bank.read_text()
    assert all(checks.values()),checks
    result=dict(result='PARTIAL',scope=__doc__,checks=checks,checks_passed=passed+len(checks),reports_sha256=reports,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                genuine_installed_save_profiles=2,actual_failed_f5_cases=3,compared_native_video_and_full_wram_fields=360,
                independent_complete_client_notification_pixels=pixels,legacy_rejection_preserves_live_timeline_and_files=True,
                current_format_replay_exact_within_each_private_build=True,current_native_saves_load_in_preceding_native_player=True,
                stable_cross_update_private_save_identity=False,legacy_save_migration_verified=False,
                native75_and_allbugs_retained_by_unchanged_core=True,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-legacy-save-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL legacy handling:',result['checks_passed'],'checks;',pixels,'independent client pixels',flush=True)


if __name__=='__main__':main()
