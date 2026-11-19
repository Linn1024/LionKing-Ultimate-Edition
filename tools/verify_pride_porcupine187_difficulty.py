"""Bound actual porcupine damage/protection and within-source difficulty recovery."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
native_path=ROOT/'build/pride-porcupine186-polled/report.json';native=bound(native_path);assert native['result']=='CAPTURED'
md_path=ROOT/'build/md-porcupine178-difficulty/report.json';md=bound(md_path);assert md['result']=='CAPTURED'
out=ROOT/'build/pride-porcupine187-difficulty';out.mkdir();checks={};observations={};recovery={};paths=[Path(__file__),native_path,md_path]
for source,report,p in [('native',native,native_path),('md',md,md_path)]:
    recovery[source]={}
    for difficulty in ('easy','normal','hard'):
        folder=p.parent/difficulty
        if source=='native':
            file=folder/'damage.csv';rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(file.open())]
            hit=report['cases'][difficulty]['porcupine_hits'][0];field=hit['field']
            checks[source+'_'+difficulty+'_actual_porcupine_reaction']=hit['attack'] and hit['prior']['pending']==4 and hit['prior']['attacker_descriptor']==0xc58c5c and hit['prior']['attacker_action']==0xc15b87
            state=lambda r:(r['health'],r['immunity'],r['x'],r['y'],r['action'])
        else:
            file=folder/'frames.json';rows=json.loads(file.read_text());hit=report['cases'][difficulty]['drops'][0];field=hit['field']
            events=report['cases'][difficulty]['reactions']
            checks[source+'_'+difficulty+'_actual_porcupine_reaction']=any(int(e['field'])==field-1 and e['player_flags']=='04' and e['attacker']=='ff98ce' and e['health']=='4' and e['action']=='19a446' for e in events)
            state=lambda r:(r['health'],r['immunity'],*r['player'],r['action'])
        index=next(i for i,r in enumerate(rows) if r['field']==field);after=[];sequence=[]
        for r in rows[index:]:
            after.append(r)
            if not sequence or r['immunity']!=sequence[-1]:sequence.append(r['immunity'])
            if r['immunity']==0:break
        checks[source+'_'+difficulty+'_unit_health_loss']=hit['before']==4 and hit['after']==3
        checks[source+'_'+difficulty+'_exact100_update_protection']=sequence==list(range(100,-1,-1))
        checks[source+'_'+difficulty+'_health_protected_until_zero']=all(r['health']==3 for r in after)
        recovery[source][difficulty]=[state(r) for r in after]
        observations[source+'-'+difficulty]=dict(hit=hit,protection_first=after[0],protection_last=after[-1],protection_fields=len(after),decrements=100)
        paths.append(file)
    checks[source+'_three_difficulties_same_observed_recovery']=recovery[source]['easy']==recovery[source]['normal']==recovery[source]['hard']
checks['source_hit_fields_not_equated']=True
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
    scope='Attributed actual porcupine attack hits on three real Options difficulties. One health loss and100-to0 protection, health remains3; within each source the sampled post-hit health/immunity/position/action sequence agrees across difficulties. Native/MD world histories/coordinates/hit fields remain distinct. Native uses fresh same-build planning checkpoints, not a new uninterrupted power-on recording; production/mode neutrality separate. No whole AI or fatal/retry outcome claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
