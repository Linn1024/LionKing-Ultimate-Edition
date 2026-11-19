"""Bind the one-pass frontend and its actual mixed/native window evidence."""
import json
import csv
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-singlepass';paths=[Path(__file__)];reports={};passed=0;checks={}
    def read(path,result='PASS'):
        nonlocal passed
        r=bound(path);assert r['result']==result,(path,r['result'])
        if result=='PASS':assert all(r.get('checks',{}).values()),path;passed+=len(r.get('checks',{}))
        paths.append(path);reports[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path);return r
    prior_aggregate=read(ROOT/'build/pride-machine-reset-player-latest.json','PARTIAL');assert prior_aggregate['checks_passed']==256
    build=read(base/'build-report.json','BUILT');plain=read(base/'plain-native/build-report.json','BUILT')
    old=read(ROOT/'build/pride-machine-player4/build-report.json','BUILT');old_plain=read(ROOT/'build/pride-reset/fixed4/build-report.json','BUILT')
    for value,binary in ((build,base/'singlepass.exe'),(plain,base/'plain-native/native.exe')):
        assert digest(binary)==value['binary_sha256']
        for name,sha in value['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        for name,sha in value['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for label,a,b in (('mixed',old['link_inputs_sha256'],build['link_inputs_sha256']),('native',old_plain['runs']['sdl']['link_inputs_sha256'],plain['link_inputs_sha256'])):
        shared=set(a)&set(b);checks[label+'/unchanged_link_objects']=all(a[k]==b[k] for k in shared)
        checks[label+'/only_frontend_object_replaced']=len(set(a)-set(b))==len(set(b)-set(a))==1
    presentations=0
    for case in ('native','md'):
        r=read(base/case/'report.json');assert r['binary_sha256']==build['binary_sha256'];presentations+=r['single_overlay_pass_presentations']
    pixel_oracles=0
    for path in (base/'windows/native-owned/report.json',base/'windows/md-owned/report.json',base/'audio-windows/md-owned/report.json',base/'audio-windows/md-owned-software/report.json'):
        r=read(path);assert r['binary_sha256']==build['binary_sha256'];pixel_oracles+=r['pixels_compared']
    for case in ('native','md'):
        for presenter in ('gl','sdl'):
            r=read(base/'menus'/(case+'-'+presenter)/'report.json');assert r['binary_sha256']==build['binary_sha256']
        r=read(base/'turbo'/case/'report.json');assert r['binary_sha256']==build['binary_sha256']
        width=640 if case=='md' else 512;pixel_oracles+=width*448
    raw_native=read(base/'plain-native/verified/report.json','INCOMPLETE')
    checks['native/only_initial_status_text_mismatch']=[k for k,v in raw_native['checks'].items() if not v]==['aot-menu-gl/whole_client']
    r=read(base/'plain-native/ready-reference/report.json');assert r['binary_sha256']==plain['binary_sha256'];presentations+=r['presentations']
    remap=read(base/'remap/report.json');assert remap['binaries_sha256']==dict(mixed=build['binary_sha256'],native=plain['binary_sha256'])
    owned_bytes=0
    for case in ('native','md-media'):
        raw=read(base/'owned-ui-save'/case/'report.json','INCOMPLETE')
        assert raw['binary_sha256']==build['binary_sha256']
        checks[case+'/only_nonvisual_record_difference']=[k for k,v in raw['checks'].items() if not v]==['whole_ui_free_record']
        passed+=sum(raw['checks'].values())
        r=read(base/'owned-ui-save-audit'/case/'report.json');assert r['binary_sha256']==build['binary_sha256'];owned_bytes+=r['canonical_bytes']
    presentations=0
    for path in base.rglob('presents.csv'):
        with path.open() as stream:records=list(csv.DictReader(stream))
        assert records and all(int(r['toast_calls'])==(0 if int(r['prompt']) else 1) for r in records),path
        presentations+=len(records);paths.append(path)
    assert all(checks.values()),checks
    result=dict(result='PARTIAL',checks=checks,checks_passed=passed+len(checks),reports_sha256=reports,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        one_pass_presentations_observed=presentations,independent_toast_and_turbo_client_pixels=pixel_oracles,
        owned_save_canonical_bytes=owned_bytes,owned_save_visual_guest_audio_data_exact=True,
        owned_save_whole_record_byte_identical=False,one_pass_frontend_integrated=True,
        practice_panel_independent_pixel_oracle=False,plain_sdl_nested_resource_editing_verified=False,
        legacy_save_migration_verified=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-singlepass-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL one-pass frontend:',result['checks_passed'],'checks;',presentations,'presentations;',pixel_oracles,'oracle pixels',flush=True)


if __name__=='__main__':main()
