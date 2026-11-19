"""Bind ordered save compatibility, cross-editor replays and actual Windows F5."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from pride_save_identity2 import contract_identity


def main():
    base=ROOT/'build/pride-save-identity2';paths=[Path(__file__),ROOT/'tools/pride_save_identity.py',ROOT/'tools/pride_save_identity2.py'];reports={};passed=0;checks={}
    def read(path,result='PASS'):
        nonlocal passed
        r=bound(path);assert r['result']==result,(path,r['result'])
        if result=='PASS':assert all(r['checks'].values()),path;passed+=len(r['checks'])
        paths.append(path);reports[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path);return r
    prior=read(ROOT/'build/pride-legacy-save-latest.json','PARTIAL');assert prior['checks_passed']==88
    build=read(base/'build-report.json','BUILT');old=read(ROOT/'build/pride-legacy-save/player/build-report.json','BUILT')
    for label,value in build['runs'].items():
        assert digest(base/(label+'.exe'))==value['binary_sha256']
        for name,sha in value['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        a,b=old['runs']['mixed']['link_inputs_sha256'],value['link_inputs_sha256'];shared=set(a)&set(b)
        checks[label+'/unchanged_link_objects']=all(a[k]==b[k] for k in shared)
        checks[label+'/only_frontend_replaced']=len(set(a)-set(b))==len(set(b)-set(a))==1
        manifest=base/(label+'-compatibility.json');paths.append(manifest)
        contract=json.loads(manifest.read_text());checks[label+'/identity_matches_contract']=contract['schema']==2 and contract_identity(contract)==value['save_compatibility_sha256']
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    checks['distinct_editor_binaries_same_compatibility']=build['runs']['a']['binary_sha256']!=build['runs']['b']['binary_sha256'] and build['runs']['a']['save_compatibility_sha256']==build['runs']['b']['save_compatibility_sha256']
    checks['incompatible_epoch_has_distinct_identity']=build['runs']['incompatible']['save_compatibility_sha256']!=build['runs']['a']['save_compatibility_sha256']
    fields=6000
    for profile in ('native','md'):
        r=read(base/'verified'/profile/'report.json');assert r['binary_sha256']=={label:value['binary_sha256'] for label,value in build['runs'].items()};fields+=r['native_fields_compared']
    read(base/'contract-report.json');read(base/'ui/report.json');read(base/'nested-rejection/report.json');read(base/'preceding-cold/report.json')
    scene=read(base/'scene-audit.json');live=read(base/'live-audit.json');fields+=live['native_fields_compared']
    for profile in ('native','md'):
        raw=read(base/'live'/profile/'report.json','INCOMPLETE');assert [k for k,v in raw['checks'].items() if not v]==['whole_client_oracle']
    assert all(checks.values()),checks
    result=dict(result='PARTIAL',scope=__doc__,checks=checks,checks_passed=passed+len(checks),reports_sha256=reports,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},native_fields_compared=fields,
                ordered_component_count=len(json.loads((base/'a-compatibility.json').read_text())['linked_components_sha256']),private_context_sources=build['private_source_count'],
                compared_scene_artifact_bytes=scene['compared_scene_artifact_bytes'],compared_rgb_artifacts=scene['compared_rgb_artifacts'],
                independent_complete_client_notification_pixels=live['independent_complete_client_pixels'],
                cross_editor_ordinary_owned_and_boot_save_replay_verified=True,actual_cross_editor_owned_f5_verified=True,
                compatibility_identity_binds_all_nonfrontend_objects=True,native75_and_allbugs_retained_by_unchanged_core=True,
                pre_contract_private_save_migration_verified=False,public_legacy_runtime7_migration_verified=False,
                public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-save-identity-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL save identity:',result['checks_passed'],'checks;',fields,'native fields;',scene['compared_scene_artifact_bytes'],'scene bytes',flush=True)


if __name__=='__main__':main()
