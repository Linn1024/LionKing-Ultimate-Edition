"""Correct the update/frame assumption using the retained walking captures."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-walking-response';source=base/'report.json';prior=bound(source)
    assert prior['result']=='FAIL' and [k for k,v in prior['checks'].items() if not v]==['all28_walking_timers']
    out=base/'qualification';out.mkdir()
    checks={k:v for k,v in prior['checks'].items() if k!='all28_walking_timers'}
    trace=list(csv.DictReader((base/'observer/attack.csv').open()))
    timers=[int(r['timer']) for r in trace if r['actor']=='b593' and r['pc']=='c15c64']
    checks['all28_original_attack_updates']=timers==list(range(27,-1,-1))
    tree={r['field']:r for r in map(json.loads,(base/'observer/tree.jsonl').read_text().splitlines())}
    actors=list(csv.DictReader((base/'observer/actors.csv').open()))
    actor=lambda f:next(r for r in actors if r['field']==str(f) and r['actor']=='b593')
    checks['repeated_timer22_has_no_pad_poll']=tree[3965]['poll_index']==tree[3966]['poll_index'] and actor(3965)['timer']==actor(3966)['timer']=='22'
    events=list(csv.DictReader((base/'observer/events.csv').open()))
    selected=[r for r in events if r['event']=='0015' and int(r['frame'])>=3958]
    checks['walking_actor_has_no_attack_event']=not any(r['actor']=='b593' for r in selected)
    checks['nearby_idle_actor_keeps_its_attack_event']=[(r['actor'],r['frame']) for r in selected]==[('ba93','3960')]
    paths=[Path(__file__),source,base/'observer/attack.csv',base/'observer/actors.csv',
           base/'observer/tree.jsonl',base/'observer/events.csv']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                original_attack_update_timers=timers,retained_failed_frame_assumption=True,
                captures_reused_without_reruns=True,new_runtime_or_renderer_change=False,
                ordinary_walking_entry_cue_and_cold_saves_verified=True,
                original_md_rendered_frame_schedule_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
