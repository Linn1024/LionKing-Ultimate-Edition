"""Qualify retained full-route captures, allowing the real final extra repaint."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token47/full-route';source=base/'report.json';prior=bound(source)
    assert prior['result']=='FAIL'
    assert {k for k,v in prior['checks'].items() if not v}=={'aot_completes_pride','lle_completes_pride'}
    out=base/'qualification';out.mkdir();checks={k:v for k,v in prior['checks'].items() if not k.endswith('_completes_pride')}
    for label in ('aot','lle'):
        rows=[json.loads(line) for line in (base/label/'tree.jsonl').read_text().splitlines()]
        fields=[row['field'] for row in rows]
        checks[label+'_all6000_fields_and_final_repaint']=fields==list(range(1,6001))+[6000]
        checks[label+'_final_repaint_is_same_state']=rows[-1]==rows[-2]
        checks[label+'_completes_pride_at_reference_field']=next(row['field'] for row in rows if row['level']==1)==4518 and rows[-1]['level']==1
    paths=[Path(__file__),source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                original_failed_assertions_preserved=True,captures_reused_without_rerun=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
