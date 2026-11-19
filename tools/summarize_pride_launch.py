"""Bind normal configuration, independent death timing, native routes and preview entry."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from pride_save_identity2 import contract_identity


def main():
    base=ROOT/'build/pride-launch2';paths=[Path(__file__)];reports={};passed=0;checks={}
    def read(path,result='PASS'):
        nonlocal passed
        r=bound(path);assert r['result']==result,(path,r['result'])
        if result=='PASS':assert all(r['checks'].values()),path;passed+=len(r['checks'])
        paths.append(path);reports[path.relative_to(ROOT).as_posix()]=digest(path);return r
    prior=read(ROOT/'build/pride-save-identity-latest.json','PARTIAL');assert prior['checks_passed']==311
    build=read(base/'build-report.json','BUILT');assert digest(base/'player.exe')==build['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in build['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    contract_path=base/'save-compatibility.json';paths.append(contract_path)
    checks['compiled_compatibility_contract']=contract_identity(json.loads(contract_path.read_text()))==build['save_compatibility_sha256']
    probe=read(base/'probe/report.json');switch=read(base/'switch/report.json');slots=read(base/'preview-slots/report.json');read(base/'save-sources/report.json')
    read(base/'preview-package-audit.json');read(base/'launcher-audit.json')
    # Bind the smoke's exact artifacts and controlled input snapshots through
    # its audit; live user settings intentionally remain free to change.
    smoke_path=base/'launcher-smoke/report.json';smoke=json.loads(smoke_path.read_text());assert smoke['result']=='PASS' and all(smoke['checks'].values());paths.append(smoke_path)
    for name,sha in smoke['artifacts_sha256'].items():assert digest(smoke_path.parent/name)==sha,name
    baseline_path=ROOT/'build/pride-reset/fixed4/native/gates/play-report.json';baseline=json.loads(baseline_path.read_text());paths.append(baseline_path)
    gates_path=base/'native-gates/play-report.json';gates=json.loads(gates_path.read_text());paths.append(gates_path)
    verifier=ROOT/'tools/verify_pride_launch_native.py';original=ROOT/'tools/verify_native_routes.py';paths.extend([verifier,original])
    assert gates['result']=='PASS' and gates['binary_sha256']==build['binary_sha256'] and gates['verifier_sha256']==digest(verifier)
    checks['native75_route_count']=gates['route_count']==baseline['route_count']==75
    for name,value in gates['routes'].items():
        checks['native/'+name]=value['aot']==value['lle']==baseline['routes'][name]['aot']==baseline['routes'][name]['lle']
        for mode in ('aot','lle'):
            log=base/'native-gates'/(name+'-'+mode+'.log');paths.append(log)
            actual=dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',log.read_text(),re.M));assert actual==value[mode],(name,mode)
    first=read(ROOT/'build/pride-launch/probe/report.json','INCOMPLETE')
    failures={k for k,v in first['checks'].items() if not v}
    checks['preserved_initial_native_dispatch_failure']=failures=={case+'/'+key for case in ('native-aot','native-lle') for key in ('after/exit','all_guest_fields','complete_pcm','whole_client','whole_guest')}
    checks['preview_binary_exact']=digest(ROOT/'dist/development-preview/LionKing.exe')==build['binary_sha256']
    assert all(checks.values()),checks
    result=dict(result='PARTIAL',scope=__doc__,checks=checks,checks_passed=passed+len(checks),reports_sha256=reports,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},compared_native_video_and_full_wram_fields=12000+switch['native_fields_compared']+slots['native_fields_compared'],
                native_route_endpoints=75,resource_health_death_selection_verified=True,normal_launch_requires_no_research_settings=True,
                native_without_md_rom_verified=True,actual_mode_changes_restart_and_restore_native=True,actual_f1_f5_without_research_settings_verified=True,
                experimental_preview_available=True,preview_launcher='Play Development Preview.cmd',default_installed_player_replaced=False,
                production_cmake_integration_complete=False,allbugs_every_field_rerun_on_this_host=False,legacy_save_migration_verified=False,
                full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-launch-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL normal-launch preview:',result['checks_passed'],'checks;',result['compared_native_video_and_full_wram_fields'],'native fields;75 native endpoints',flush=True)


if __name__=='__main__':main()
