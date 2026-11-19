"""Bind the retained normal-mode failure and identify missing compiled hook scope."""
import json
from pathlib import Path

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def main():
    out=ROOT/'build/pride-title-upload-modes-bindings';out.mkdir();checks={}
    source=ROOT/'build/pride-title-upload-modes5/report.json';report=bound(source)
    prior=ROOT/'build/pride-title-upload-bindings/report.json';bound(prior)
    checks['mode_report_bound']=True;checks['preceding_evidence_bound']=True
    checks['normal_mode_failure_retained']=report['result']=='FAIL' and sum(report['checks'].values())==2 and len(report['checks'])==10
    for width in (256,320):
        checks[f'{width}_normal_path_has_no_slice']=report['observations'][str(width)]==dict(first_title=435,copies=0)
    manifest=ROOT/'engine/recomp/pride_final_hooks.json';info=json.loads(manifest.read_text())
    checks['bulk_hook_not_generated']='0xc22036' not in info['hook_pcs']
    checks['bulk_unit_not_in_final_extension']='bankc2_part14_v2.c' not in info['instrumented_units']
    paths=[Path(__file__),source,prior,manifest]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                scope='Confirms research LLE success does not establish normal compiled integration',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(result['result'],sum(checks.values()),'/',len(checks),flush=True);assert all(checks.values())

if __name__=='__main__':main()
