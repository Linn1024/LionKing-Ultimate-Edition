"""Separate opening-card, Pride, and next-level sound calls in the frozen route."""
from collections import Counter
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-audio-dispatch75/report.json';p=bound(prior)
    assert p['result']=='CURRENT_DISPATCH_INVENTORIED' and all(p['checks'].values())
    events=prior.parent/'events.csv';rows=list(csv.DictReader(events.open()))
    main=[r for r in rows if r['level']=='0000' and r['descriptor'] in ('0387','080d')]
    first_main=min(int(r['frame']) for r in main)
    title=[r for r in rows if r['level']=='0000' and r['descriptor']=='05ab' and int(r['event'],16)>2]
    later=[r for r in rows if r['level']=='0001' and int(r['event'],16)>2]
    other=[r for r in rows if int(r['event'],16)>2 and r not in main and r not in title and r not in later]
    def groups(items):
        counts=Counter()
        for r in items:
            raw=bytes.fromhex(r['stack'])
            offset={'2d16':5,'2d4d':6}.get(r['return0'])
            assert offset is not None
            caller=(int.from_bytes(raw[offset:offset+3],'little')+1)&0xffffff
            counts[(r['level'],r['descriptor'],r['event'],f'{caller:06x}')]+=1
        return [dict(level=k[0],descriptor=k[1],event=k[2],caller=k[3],count=v) for k,v in sorted(counts.items())]
    checks=dict(prior_seven_checks_bound=True,
                six_opening_card_effect_calls=len(title)==6,
                all_card_effects_precede_pride=all(int(r['frame'])<first_main for r in title),
                five_opening_card_callers=len(groups(title))==5,
                ten_next_level_effect_calls=len(later)==10,
                all_next_level_calls_after_pride=all(int(r['frame'])>max(int(r['frame']) for r in main) for r in later),
                next_level_descriptor03b9=all(r['descriptor']=='03b9' for r in later),
                no_remaining_other_effect_calls=not other)
    out=ROOT/'build/pride-audio-scene76';out.mkdir()
    paths=[Path(__file__),prior,events]
    report=dict(result='SCENE_SCOPES_CLASSIFIED' if all(checks.values()) else 'FAIL',checks=checks,
                first_main_audio_event_field=first_main,
                opening_card_groups=groups(title),next_level_groups=groups(later),other_groups=groups(other),
                opening_card_field_range=[min(int(r['frame']) for r in title),max(int(r['frame']) for r in title)],
                next_level_is_not_a_missing_pride_effect=True,
                card_synthesis_or_md_equivalence_proven=False,bonus_coverage_proven=False,
                scope='Frozen audio event classification only. No new runtime or original MD execution.',
                source_sha256={path.relative_to(ROOT).as_posix():digest(path) for path in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),groups(title),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
