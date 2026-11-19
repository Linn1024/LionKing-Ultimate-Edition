"""Account for the saved health row before the first cold-rendered row."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-contact-verification2';out.mkdir()
    source=ROOT/'build/pride-porcupine-contact-verification/report.json';old=bound(source)
    assert len(old['checks'])==57 and sum(old['checks'].values())==56 and not old['checks']['pending_cold_one_damage']
    base=ROOT/'build/pride-porcupine38'
    seed=base/'contact-pending/tree.jsonl';cold=base/'contact-pending-cold/tree.jsonl'
    before=json.loads(seed.read_text().splitlines()[-1])
    rows=[before]+[json.loads(line) for line in cold.read_text().splitlines()]
    drops=[(b['field'],a['health'],b['health']) for a,b in zip(rows,rows[1:]) if b['health']<a['health']]
    checks=old['checks'].copy();checks['pending_cold_one_damage']=drops==[(1472,4,3)]
    checks['saved_row_precedes_cold_row']=before['field']==1471 and rows[1]['field']==1472
    checks['first_failure_retained']=old['result']=='FAIL'
    paths=[Path(__file__),source,seed,cold]
    # Validate every source report used by the completed original runs.
    for name in old['source_sha256']:
        if name.endswith('/report.json') or name.endswith('/build-report.json'):bound(ROOT/name)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                correction='Cold capture starts after damage consumption; prepend the actual saved health row to test the transition.',
                pending_cold_damage=drops,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
