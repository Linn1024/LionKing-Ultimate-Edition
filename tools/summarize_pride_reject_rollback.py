"""Bind scoped live rejected-load rollback evidence without public activation."""
import concurrent.futures
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_handoff_state import rows
from probe_pride_reject_rollback import BASE
from run_pride_reject_rollback_matrix import CASES,WINDOWS,case_name
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data
from run_pride_actor_handoff_matrix import CONTEXTS


def bound(path):
    r=json.loads(path.read_text())
    for file,sha in r['source_sha256'].items():assert digest(ROOT/file)==sha,(path,file)
    return r


def verify(job):
    host,case=job;folder=BASE/host/case_name(case);r=bound(folder/'report.json')
    assert r['result']=='PASS' and not r['full_first_level_fidelity_complete'] and not r['public_player_enabled'],folder
    variants=['preflight','forced'] if host=='windows' else (['preflight','history','cache','backend','forced'] if case==CASES[0] else ['backend','forced'])
    assert set(r['cases'])=={'control',*variants},folder
    context,width,graphics,save,fault,mode=case
    assert (r['context'],r['width'],r['graphics'],r['mode'])==(context,width,graphics,mode),folder
    entry=CONTEXTS[context][3]-(345 if context=='snes-checkpoint' else 300)
    assert r['save_at']==entry+save and r['fault_at']==entry+fault
    binary=BASE/f"rollback-{'sdl' if host=='windows' else 'probe'}.exe";assert digest(binary)==r['binary_sha256'],folder
    control=folder/'control'
    for name,run in r['cases'].items():
        part=folder/name
        assert run['result']=='PASS' and run['exit_code']==0 and all(run['checks'].values()),(folder,name)
        for file,sha in run['artifacts_sha256'].items():assert digest(part/file)==sha,(folder,name,file)
        event=rows(part/'rejected-load.csv')[0];assert event==run['event'] and int(event['field'])==r['fault_at']
        assert event['returned']=='0' and int(event['caller_field'])==0xdecafbad
        for section in ('native','context','history','cache'):
            a,b=digest(part/f'reject-before.{section}'),digest(part/f'reject-after.{section}')
            assert a==b and [a,b]==run['snapshots'][section],(folder,name,section)
        if name=='forced':
            assert event['native_calls']=='1' and event['native_successes']=='0'
            assert event['backend_calls']==event['backend_successes']=='2' and event['injected']=='1'
        elif name=='backend':
            assert event['native_calls']=='1' and event['native_successes']=='0'
            assert event['backend_calls']=='2' and event['backend_successes']=='1' and event['injected']=='0'
        else:assert event['native_calls']==event['backend_calls']=='0'
        if name!='control':
            assert hashes(part/'run.log')==hashes(control/'run.log') and len(hashes(part/'run.log'))==2
            image='window.png' if host=='windows' else 'picture.png'
            assert pixels(part/image)==pixels(control/image),(folder,name,'client')
            if host=='windows':assert wav_data(part/'audio.wav')==wav_data(control/'audio.wav'),(folder,name,'PCM')
    return dict(host=host,case=case_name(case),report_sha256=digest(folder/'report.json'),
                runs=len(r['cases']),rejected_loads=len(r['cases'])-1,forced_native_restores=1)


def main():
    build=bound(BASE/'build-report.json')
    for file,sha in build['production_sha256'].items():assert digest(ROOT/file)==sha,file
    for host,r in build['runs'].items():
        assert digest(BASE/f'rollback-{host}.exe')==r['binary_sha256']
        for file,sha in r['link_inputs_sha256'].items():assert digest(ROOT/file)==sha,file
    jobs=[('headless',case) for case in CASES]+[('windows',case) for case in WINDOWS]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(verify,jobs))
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),ROOT/'tools/run_pride_reject_rollback_matrix.py',ROOT/'tools/verify_windows.py',
        ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/run_pride_actor_handoff_matrix.py',BASE/'build-report.json')}
    out=dict(result='PARTIAL',scope='Same-process loader calls at the final pre-CPU wrapper boundary; native, private context, history/cache snapshots and continuation.',
        cases=results,source_sha256=sources,game_runs=sum(r['runs'] for r in results),
        rejected_loads=sum(r['rejected_loads'] for r in results),successful_native_restore_then_rejection_cases=8,
        scoped_failed_load_rollback_verified=True,actual_f1_error_ui_verified=False,source_switch_lifecycle_verified=False,
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-reject-rollback-latest.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('cases','source_sha256')},indent=2),flush=True)


if __name__=='__main__':main()
