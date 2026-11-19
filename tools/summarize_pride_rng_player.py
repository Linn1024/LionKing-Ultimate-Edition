"""Bind the entry-RNG integration, original grounding and bounded native gates."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    one=ROOT/'build/pride-rng-player';two=ROOT/'build/pride-rng-player2'
    paths=[Path(__file__)];reports={};checks=0;fields=0
    builds=[]
    for folder in (one,two,two/'allbugs-observer'):
        p=folder/'build-report.json';r=bound(p);assert r['result']=='BUILT'
        assert digest(folder/'player.exe')==r['binary_sha256']
        for name,sha in r['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        for name,sha in r.get('production_sha256',{}).items():assert digest(ROOT/name)==sha,name
        paths.append(p);builds.append(r)
    cores=[]
    for r in builds:
        cores.append({k:v for k,v in r['link_inputs_sha256'].items() if not k.endswith('/host.obj')})
    assert cores[0]==cores[1]==cores[2], 'Core drift between player generations/observer'
    def passing(path,expected_checks,expected_fields):
        nonlocal checks,fields
        r=bound(path)
        assert r['result']=='PASS' and len(r['checks'])==expected_checks and all(r['checks'].values()),path
        actual=r.get('native_fields_compared',r.get('compared_fields'))
        assert actual==expected_fields,(path,actual)
        checks+=expected_checks;fields+=expected_fields;paths.append(path)
        reports[path.relative_to(ROOT).as_posix()]=dict(result='PASS',checks=expected_checks,compared_fields=expected_fields)
        return r
    for relative,count,nfields in (
        ('regression/report.json',20,12000),('source/report.json',22,5800),
        ('rng-switch/report.json',11,7001),('rng-private-slots/report.json',8,1711)):
        passing(one/relative,count,nfields)
    passing(two/'regression/report.json',20,12000)
    passing(two/'ground-window-audit.json',18,4700)
    passing(two/'allbugs2/report.json',9,60648)
    native_path=one/'native-gates/play-report.json';native=json.loads(native_path.read_text())
    baseline_path=ROOT/'build/pride-reset/fixed4/native/gates/play-report.json'
    baseline=json.loads(baseline_path.read_text())
    assert native['result']=='PASS' and native['route_count']==75
    assert native['routes']==baseline['routes'] and baseline['result']=='PASS'
    assert native['binary_sha256']==builds[0]['binary_sha256']
    assert native['verifier_sha256']==digest(ROOT/'tools/verify_pride_rng_native_routes.py')
    paths.extend([native_path,baseline_path,ROOT/'tools/verify_pride_rng_native_routes.py',
                  ROOT/'tools/verify_pride_launch_native.py',ROOT/'tools/verify_native_routes.py'])
    for r in native['routes'].values():assert r['aot']==r['lle']
    failure_path=one/'completion-failure/report.json';failure=bound(failure_path)
    assert failure['runs']=={m:dict(exit=87,last_field=4651) for m in ('aot','lle')}
    paths.append(failure_path)
    incomplete={}
    for relative,expected_missing in (
        ('completion/report.json',{f'{w}/{m}/{check}' for w in (256,320) for m in ('aot','lle')
          for check in ('next_main_level','level_and_boss_music')}),
        ('completion-reference/report.json',{'320/aot/next_main_level','320/lle/next_main_level'})):
        path=two/relative;r=bound(path)
        missing={k for k,v in r['checks'].items() if not v}
        assert r['result']=='INCOMPLETE' and missing==expected_missing
        assert r['ordinary_poweron_controller_inputs_only'] and not r['loaded_states'] and not r['practice_or_guest_edits']
        paths.append(path);incomplete[relative]=sorted(missing)
    # Actual inspected OS captures are evidence distinct from guest-state hashes.
    for p in (one/'rng-switch/live/pending-md.png',one/'rng-private-slots/live/client.png',
              two/'completion/320/aot/window.png',two/'completion-reference/320/aot/window.png'):
        assert p.is_file();paths.append(p)
    preview=ROOT/'dist/development-preview/LionKing.exe'
    assert digest(preview)==digest(ROOT/'build/pride-launch2/player.exe')
    paths.append(preview)
    report=dict(result='PARTIAL',checks=checks,compared_fields=fields,
        native_route_endpoints=75,native_allbugs_fields=60648,passing_reports=reports,
        retained_incomplete_routes=incomplete,grounding_original_instructions=144,
        all_nonhost_link_inputs_identical=True,public_preview_unchanged=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        full_rng_on_mixture_completion_verified=False,full_first_level_fidelity_complete=False,
        public_player_enabled=False)
    output=ROOT/'build/pride-rng-player-latest.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL',checks,'checks;',fields,'compared fields; native75/All Bugs verified',flush=True)


if __name__=='__main__':main()
