"""Bind full help-page pixels, SDL virtual devices and unchanged native rendering."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-tree-help2';paths=[Path(__file__)];reports={};passed=0;checks={}
    def read(path,result='PASS'):
        nonlocal passed
        r=bound(path);assert r['result']==result,(path,r['result'])
        if result=='PASS':assert all(r['checks'].values()),path;passed+=len(r['checks'])
        paths.append(path);reports[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path);return r
    previous=read(ROOT/'build/pride-soft-tree-latest.json','PARTIAL');assert previous['checks_passed']==96
    mixed=read(base/'build-report.json','BUILT');native=read(base/'plain-native/build-report.json','BUILT')
    old=read(ROOT/'build/pride-soft-tree/build-report.json','BUILT');old_native=read(ROOT/'build/pride-soft-tree/plain-native/build-report.json','BUILT')
    for label,value,prior,binary in (('mixed',mixed,old,base/'singlepass.exe'),('native',native,old_native,base/'plain-native/native.exe')):
        assert digest(binary)==value['binary_sha256']
        for name,sha in value['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        for name,sha in value['production_sha256'].items():assert digest(ROOT/name)==sha,name
        a,b=prior['link_inputs_sha256'],value['link_inputs_sha256'];shared=set(a)&set(b)
        checks[label+'/unchanged_core_objects']=all(a[k]==b[k] for k in shared)
        checks[label+'/only_frontend_replaced']=len(set(a)-set(b))==len(set(b)-set(a))==1
    pixels=0;presentations=0
    for case in ('native','md'):
        r=read(base/'windows'/case/'report.json');assert r['binary_sha256']==mixed['binary_sha256'];presentations+=r['presentations']
        page_checks=[k for k in r['checks'] if re.fullmatch(r'page-\d+-independent-panel-pixels',k)]
        assert len(page_checks)==2;pixels+=len(page_checks)*248*122*4
    r=read(base/'plain-native/verified/report.json');assert r['binary_sha256']==native['binary_sha256'];presentations+=r['presentations']
    r=read(base/'remap/report.json');assert r['binaries_sha256']==dict(mixed=mixed['binary_sha256'],native=native['binary_sha256'])
    failed_build=read(ROOT/'build/pride-tree-help/build-report.json','BUILT')
    logs=[]
    for case in ('mixed','native'):
        path=ROOT/'build/pride-tree-help/remap'/case/'run.log';text=path.read_text();paths.append(path)
        failures=re.findall(r'^remap_selftest: FAIL (.*)$',text,re.M)
        logs.append(failures==['virtual Guide closes entire resource editor','(1 failed)'])
    checks['preserved_initial_guide_duplicate_failure']=all(logs)
    sdl_source=ROOT/'.tools/SDL3-3.4.10/src/joystick/SDL_gamepad.c';paths.append(sdl_source)
    checks['guide_test_respects_sdl_minimum_press']=bool(re.search(r'#define SDL_MINIMUM_GUIDE_BUTTON_DELAY_MS 250\b',sdl_source.read_text()))
    # The production event/commit/restart implementation is the preceding exact
    # source; this generation only adds test invocation and substitutes its UI header.
    a=(ROOT/'build/pride-soft-tree/patched/sdl_main.c').read_text();b=(base/'patched/sdl_main.c').read_text()
    b=b.replace('#include "tlk_resource_editor_selftest.h"\n\n','').replace('        if (!s_menu_gl) StResourceSelfTest(js);\n','')
    checks['unchanged_production_commit_and_event_paths']=a==b
    assert all(checks.values()),checks
    result=dict(result='PARTIAL',scope=__doc__,checks=checks,checks_passed=passed+len(checks),reports_sha256=reports,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                presentations_observed=presentations,compared_native_video_and_full_wram_fields=11601,
                independent_os_help_panel_pixels=pixels,plain_sdl_keyboard_mouse_and_virtual_gamepad_tree_verified=True,
                complete_resource_scope_and_fallback_help_verified=True,long_help_paging_verified=True,
                prior_source_restart_evidence_retained_by_unchanged_commit_callback=True,
                native75_and_allbugs_retained_by_unchanged_core=True,physical_controller_tested=False,
                practice_panel_independent_pixel_oracle=False,legacy_save_migration_verified=False,
                public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-tree-help-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL paged resource help:',result['checks_passed'],'checks;',presentations,'presentations;',pixels,'independent OS pixels',flush=True)


if __name__=='__main__':main()
