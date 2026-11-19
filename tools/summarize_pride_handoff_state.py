"""Bind default/checkpoint preparation and normal-publication save evidence."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from run_pride_actor_handoff_matrix import CONTEXTS
from run_pride_handoff_state_matrix import cases,case_name
from probe_pride_handoff_state import BASE


def read_bound(path):
    r=json.loads(path.read_text())
    for name,sha in r['source_sha256'].items():assert digest(ROOT/name)==sha,(path,name)
    return r


def verify_case(item):
    host,job=item;path=BASE/host/case_name(job);r=read_bound(path/'report.json')
    context,width,graphics,age,save,load=job
    expected_at=CONTEXTS[context][3]-(345 if context=='snes-checkpoint' else 300)+age
    assert r['result']=='PASS' and r['checks'] and all(r['checks'].values()),path
    assert (r['context'],r['width'],r['graphics'],r['save_at'],r['save_mode'],r['load_mode'])==(
        context,width,graphics,expected_at,save,load),path
    assert r['host']==('probe' if host=='headless' else 'sdl'),path
    assert not r['guest_fixture_edits'] and r['loaded_state_only_from_current_ordinary_run'],path
    assert not r['public_player_enabled'] and not r['full_first_level_fidelity_complete'],path
    build=json.loads((BASE/'build-report.json').read_text())
    assert r['binary_sha256']==build['runs'][r['host']]['binary_sha256'],path
    for name,run in r['runs'].items():
        assert run['exit_code']==0 and len(run['guest'])==2,(path,name)
        for file,sha in run['artifacts_sha256'].items():assert digest(path/name/file)==sha,(path,name,file)
    assert digest(path/'revival.private-state')==r['state_sha256'],path
    reference=ROOT/'build/pride-actor-handoff/active'/f'{context}-{width}-{graphics}-aot-owned'
    assert (path/'resources.ini').read_bytes()==(reference/'resources.ini').read_bytes(),path
    _,route,kind,_,_=CONTEXTS[context]
    if kind=='polled':
        tape=reference/('checkpoint.polled.tape' if route=='checkpoint' else 'default-neutral.tape')
        ram=(reference if host=='windows' else path/'baseline')/'route.ram'
        cut=sum(line.split()[1]=='0' for line in ram.read_text().splitlines() if int(line.split()[0])<=expected_at)
        assert (path/'resume.tape').read_bytes()==tape.read_bytes()[cut*2:],path
    state=(path/'revival.private-state').read_bytes()
    assert state[:8]==b'PRHSAVE1' and struct.unpack_from('<I',state,12)[0]==768
    assert struct.unpack_from('<I',state,20)[0]==expected_at
    top={p.name:digest(p) for p in path.iterdir() if p.is_file() and p.name!='report.json'}
    raw=path/'resumed/render-owned.rgb';size=56+width*224*12
    records=0 if not raw.exists() else (raw.stat().st_size-16)//size
    return dict(case=case_name(job),host=host,save_age=age,report_sha256=digest(path/'report.json'),
        remaining_scene_record_pixels=records*width*224,top_artifacts_sha256=top)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=('headless','windows','aggregate'));args=p.parse_args()
    if args.stage!='aggregate':
        jobs=cases(args.stage)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            results=list(pool.map(verify_case,[(args.stage,job) for job in jobs]))
        sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
            Path(__file__),ROOT/'tools/run_pride_handoff_state_matrix.py',BASE/'build-report.json')}
        out=dict(result='PASS',stage=args.stage,cases=results,source_sha256=sources)
        (BASE/(args.stage+'-verification.json')).write_text(json.dumps(out,indent=2)+'\n')
        print(args.stage,len(results),'bound save/load cases PASS',flush=True);return
    build=read_bound(BASE/'build-report.json')
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for host,run in build['runs'].items():
        assert digest(BASE/f'handoff-state-{host}.exe')==run['binary_sha256']
        for name,sha in run['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    stages={name:read_bound(BASE/(name+'-verification.json')) for name in ('headless','windows')}
    for name,r in stages.items():
        assert r['result']=='PASS'
        for case in r['cases']:
            folder=BASE/name/case['case']
            assert digest(folder/'report.json')==case['report_sha256'],folder
            for file,sha in case['top_artifacts_sha256'].items():assert digest(folder/file)==sha,(folder,file)
    rejection=read_bound(BASE/'rejections.json');assert rejection['result']=='PASS' and len(rejection['cases'])==24
    assert rejection['binary_sha256']==build['runs']['probe']['binary_sha256']
    for name,r in rejection['cases'].items():
        folder=BASE/'rejections'/name
        assert digest(folder/'fixture.state')==r['fixture_sha256'] and digest(folder/'run.log')==r['log_sha256'],name
        assert r['exit_code']==(0 if name=='valid' else 8),name
    first=read_bound(BASE/'first-window.json');assert first['result']=='PASS' and set(first['cases'])=={'aot','lle'}
    for mode,r in first['cases'].items():
        assert r['exit_code']==0 and len(r['guest'])==2 and r['pcm_bytes']>0,mode
        for name,sha in r['artifacts_sha256'].items():assert digest(BASE/'first-window'/mode/name)==sha,(mode,name)
    live=read_bound(BASE/'live-rewind.json');assert live['result']=='PASS' and len(live['cases'])==5
    assert live['binary_sha256']==build['runs']['sdl']['binary_sha256']
    for name,r in live['cases'].items():
        assert r['result']=='PASS' and all(r['checks'].values()),name
        folder=BASE/'live-rewind'/name
        for file,sha in r['top_artifacts_sha256'].items():assert digest(folder/file)==sha,(name,file)
        for epoch,run in r['runs'].items():
            assert run['exit_code']==0 and len(run['guest'])==2,(name,epoch)
            for file,sha in run['artifacts_sha256'].items():assert digest(folder/epoch/file)==sha,(name,epoch,file)
    out=dict(result='PARTIAL',scope='Private same-profile new-process saves across default/checkpoint preparation and normal actor publication.',
        reports_sha256={n:digest(BASE/(n+'-verification.json')) for n in stages},
        rejections_sha256=digest(BASE/'rejections.json'),first_loaded_windows_sha256=digest(BASE/'first-window.json'),
        live_rewind_sha256=digest(BASE/'live-rewind.json'),live_rewinds=len(live['cases']),
        cases={n:len(r['cases']) for n,r in stages.items()},
        remaining_scene_record_pixels=sum(c['remaining_scene_record_pixels'] for r in stages.values() for c in r['cases']),
        private_new_process_save_verified=True,first_loaded_windows_verified=True,private_live_rewind_verified=True,
        same_process_rollback_verified=False,source_switch_lifecycle_verified=False,
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-handoff-state-latest.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2),flush=True)


if __name__=='__main__':main()
