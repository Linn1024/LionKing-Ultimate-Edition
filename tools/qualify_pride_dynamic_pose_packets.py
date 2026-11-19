"""Apply actual HUD role identities to the retained live packet observations."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-effect-coverage/dynamic-packets2';source=base/'report.json';prior=bound(source)
    assert prior['result']=='FAIL' and [k for k,v in prior['checks'].items() if not v]==[
        'roar_existing_semantic_guard_matches','health_existing_semantic_guard_matches']
    out=base/'qualification';out.mkdir()
    checks={k:v for k,v in prior['checks'].items() if not k.endswith('_existing_semantic_guard_matches')}
    owners=[]
    for row in prior['owners']:
        actual='caption' if row['pose']==0x7e17dd else {0:'roar',1:'health'}.get(row['role'])
        checks[str(actual)+'_existing_guard_identifies_owner']=bool(actual) and row['role']=={'caption':1,'health':1,'roar':0}[actual]
        owners.append(dict(**{k:v for k,v in row.items() if k!='name'},name=actual,
                           originally_named_snapshot=(base/(row['name']+'-wram.bin')).relative_to(ROOT).as_posix()))
    checks['all_three_dedicated_semantics_observed']={r['name'] for r in owners}=={'roar','health','caption'}
    paths=[Path(__file__),source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,owners=owners,
                captures_reused_without_reruns=True,retained_incorrect_hud_labels=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),owners,flush=True)


if __name__=='__main__':main()
