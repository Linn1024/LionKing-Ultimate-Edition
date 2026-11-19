"""Bind repeated-fight evidence and compare the second Difficult hurt response."""
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from capture_pride_difficulty_start import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-hyena-recovery';out=base/'repeated-hit-audit';out.mkdir(exist_ok=False)
    verified=base/'verification2/report.json';report=bound(verified)
    assert all(report['checks'].values())
    captures=[base/s/'report.json' for s in ('snes','md')]
    for path in captures:bound(path)
    data={s:json.loads((base/s/'hard/frames.json').read_text()) for s in ('snes','md')}
    starts={}
    for source,rows in data.items():
        action=0xc1470f if source=='snes' else 0x19b904
        entries=[i for i,r in enumerate(rows) if r['action']==action and (i==0 or rows[i-1]['action']!=action)]
        assert len(entries)==2
        starts[source]=entries[1]
    a=data['snes'][starts['snes']:starts['snes']+34]
    b=data['md'][starts['md']:starts['md']+34]
    catalog=ROOT/'tools/pride_npc_pairs.json'
    pairs={int(r['snes'],16):int(r['md'],16) for r in json.loads(catalog.read_text())['pairs'] if r['role']=='hyena'}
    checks=dict(second_hurt_33_actions=all(x['action']==0xc1470f and y['action']==0x19b904 for x,y in zip(a[:33],b[:33])),
        second_hurt_33_pose_pairs=all(pairs.get(x['pose'])==y['pose'] for x,y in zip(a[:33],b[:33])),
        second_hurt_parameters_and_relative_motion=all(
            all(x[k]==y[k] for k in ('health','cycle','tag','facing')) and
            all(x[k]-a[0][k]==y[k]-b[0][k] for k in ('x','y')) for x,y in zip(a[:33],b[:33])),
        second_hurt_wait_entry=a[33]['action']==0xc13c83 and b[33]['action']==0x19adc0 and a[33]['timer']==b[33]['timer']==119)
    assert all(checks.values()),checks
    paths=[Path(__file__),verified,*captures,catalog]
    result=dict(result='BOUNDED_REPEATED_HYENA_FIGHTS_VERIFIED',checks=checks,
        preceding_checks=len(report['checks']),total_checks=len(checks)+len(report['checks']),
        second_hurt_fields=dict(snes=a[0]['field'],md=b[0]['field']),
        retained_unused_timer_values=dict(snes=a[0]['timer'],md=b[0]['timer']),
        unused_timer_difference_requires_game_patch=False,full_enemy_equivalence=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],result['total_checks'],'checks',flush=True)


if __name__=='__main__':main()
