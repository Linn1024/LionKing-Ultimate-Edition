"""Diagnose held-input handoff after the selected-start default revival.

This polled route is not a matched original-MD input-timing experiment.
"""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_prepared_state import rows


def main():
    base=ROOT/'build/pride-spawn-revival';out=base/'active-handoff';out.mkdir(exist_ok=True)
    logs=out/'driver-logs';logs.mkdir(exist_ok=True)
    build=json.loads((base/'build-report.json').read_text())
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    def capture(job):
        graphics,mode=job;name=graphics+'-'+mode;folder=out/name;folder.mkdir(exist_ok=True)
        command=[sys.executable,str(ROOT/'tools/probe_pride_spawn_revival.py'),'--start','md','--width','320',
            '--route','checkpoint','--graphics',graphics,'--execution',mode,'--frames','2340','--output-root',str(folder)]
        if not (folder/'report.json').exists():
            with (logs/(name+'.log')).open('wb') as log:
                subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=False,timeout=300)
        r=json.loads((folder/'report.json').read_text());rendered=rows(folder/'render-fields.csv');last=rendered[-1]
        assert r['width']==320 and r['graphics']==graphics and r['execution']==mode and r['frames']==2340
        assert r['start_source']=='md' and r['route']=='checkpoint' and r['host']=='probe'
        assert not r['loaded_states'] and not r['guest_fixture_edits']
        assert r['binary_sha256']==build['runs']['probe']['binary_sha256']==digest(base/'spawn-revival-probe.exe')
        for n,sha in r['source_sha256'].items():assert digest(ROOT/n)==sha,n
        for n,sha in r['artifacts_sha256'].items():assert digest(folder/n)==sha,(name,n)
        assert all(p['checkpoint']=='0' for p in rows(folder/'spawn-policy.csv'))
        result=dict(exit_code=r['exit_code'],released=last['released']=='1',last_age=int(last['age']),last_native_pixel_mismatch=int(last['native_pixel_mismatch']),
            post_ready=rows(folder/'post-ready.csv'),capture_report_sha256=digest(folder/'report.json'))
        print(name,'released',result['released'],'last age',result['last_age'],'native mismatch',result['last_native_pixel_mismatch'],flush=True)
        return name,result
    jobs=[(g,m) for g in ('native','frames','palette','all') for m in ('aot','lle')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=dict(pool.map(capture,jobs))
    passed=all(r['exit_code']==0 and r['released'] and r['last_native_pixel_mismatch']==0 for r in results.values())
    (out/'report.json').write_text(json.dumps(dict(result='PRESENTER_HANDOFF_OBSERVED' if passed else 'ACTIVE_HANDOFF_INCOMPLETE',
        scope=__doc__,cases=results,source_sha256={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__)),
            'build/pride-spawn-revival/build-report.json':digest(base/'build-report.json')},
        original_md_input_fidelity_verified=False,full_first_level_fidelity_complete=False),indent=2)+'\n')
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
