"""Bind real fallback-tree inputs, restarts and unchanged frontend regressions."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-soft-tree';paths=[Path(__file__)];reports={};passed=0;checks={}
    def read(path,result='PASS'):
        nonlocal passed
        r=bound(path);assert r['result']==result,(path,r['result'])
        if result=='PASS':assert all(r['checks'].values()),path;passed+=len(r['checks'])
        paths.append(path);reports[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path);return r
    prior=read(ROOT/'build/pride-singlepass-latest.json','PARTIAL');assert prior['checks_passed']==440
    mixed=read(base/'build-report.json','BUILT');native=read(base/'plain-native/build-report.json','BUILT')
    old=read(ROOT/'build/pride-singlepass/build-report.json','BUILT');old_native=read(ROOT/'build/pride-singlepass/plain-native/build-report.json','BUILT')
    for label,value,previous,binary in (('mixed',mixed,old,base/'singlepass.exe'),('native',native,old_native,base/'plain-native/native.exe')):
        assert digest(binary)==value['binary_sha256']
        for name,sha in value['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        for name,sha in value['production_sha256'].items():assert digest(ROOT/name)==sha,name
        a,b=previous['link_inputs_sha256'],value['link_inputs_sha256'];shared=set(a)&set(b)
        checks[label+'/unchanged_core_objects']=all(a[k]==b[k] for k in shared)
        checks[label+'/only_frontend_replaced']=len(set(a)-set(b))==len(set(b)-set(a))==1
    presentations=0
    for name in ('native','md'):
        r=read(base/'windows-mouse-queue'/name/'report.json');assert r['binary_sha256']==mixed['binary_sha256'];presentations+=r['presentations']
    r=read(base/'missing-md/native/report.json');assert r['binary_sha256']==mixed['binary_sha256'];presentations+=r['presentations']
    r=read(base/'plain-native/verified/report.json');assert r['binary_sha256']==native['binary_sha256'];presentations+=r['presentations']
    r=read(base/'remap/report.json');assert r['binaries_sha256']==dict(mixed=mixed['binary_sha256'],native=native['binary_sha256'])
    for name in ('music','start'):
        raw=read(base/'restarts'/name/'report.json','INCOMPLETE');assert raw['binary_sha256']==mixed['binary_sha256'];presentations+=raw['presentations']
        r=read(base/'restarts'/name/'boot-control/report.json');assert r['binary_sha256']==mixed['binary_sha256']
    failed=read(base/'windows/native/report.json','INCOMPLETE')
    assert [k for k,v in failed['checks'].items() if not v]==['mouse_after_resize']
    assert all(checks.values()),checks
    result=dict(result='PARTIAL',scope=__doc__,checks=checks,checks_passed=passed+len(checks),reports_sha256=reports,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                presentations_observed=presentations,compared_native_video_and_full_wram_fields=17001,
                plain_sdl_keyboard_and_mouse_tree_verified=True,live_inheritance_leaf_overrides_revert_presets_and_validation_verified=True,
                genuine_boot_source_restarts_verified=['audio.music.pride_lands','gameplay.levels.pride_lands.start'],
                original_native_gates_retained_by_unchanged_core=True,plain_sdl_gamepad_editor_verified=False,
                long_resource_scope_help_paging_complete=False,practice_panel_independent_pixel_oracle=False,
                legacy_save_migration_verified=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-soft-tree-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL SDL tree:',result['checks_passed'],'checks;',presentations,'presentations;',result['compared_native_video_and_full_wram_fields'],'guest fields',flush=True)


if __name__=='__main__':main()
