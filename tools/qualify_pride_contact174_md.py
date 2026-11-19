"""Distinguish additional raw-slot diagnostics from changed original MD state."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/pride-contact168-md/report.json';r=bound(reference);assert r['result']=='DIFFERENCES'
fresh_path=reference.parent/'md.json';old_path=ROOT/'build/pride-roll-contacts/md.json'
fresh=json.loads(fresh_path.read_text())['cases'];old=json.loads(old_path.read_text())['cases']
out=ROOT/'build/pride-contact174-md-qualification';out.mkdir();checks={};added=set();count=0
for name,rows in fresh.items():
    same=True;extras_ok=True
    for a,b in zip(rows,old[name]):
        same &= {k:v for k,v in a.items() if k!='raw_slots'}=={k:v for k,v in b.items() if k!='raw_slots'}
        same &= len(a['raw_slots'])==len(b['raw_slots'])
        for x,y in zip(a['raw_slots'],b['raw_slots']):
            same &= all(x.get(k)==v for k,v in y.items())
            extra=x.keys()-y.keys();added.update(extra);extras_ok &= extra<= {'draw_pose','draw_attributes'}
        count+=1
    checks[name+'_all_original_recorded_fields_and_actor_words_preserved']=bool(same)
    checks[name+'_only_additional_diagnostic_fields']=bool(extras_ok)
checks['all1238_fields']=count==1238
paths=[Path(__file__),reference,fresh_path,old_path,ROOT/'tools/pride_movement_audit.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,additional_fields=sorted(added),
    correction='168 raw dictionaries differ because current raw_slots adds draw_pose/draw_attributes to suitable records. Every previously recorded field, actor/state and64 actor words remains exact across all1238 rows. Raw168 DIFFERENCES report retained. No claim that every allocated slot is active; this qualifies reference reproduction, not whole enemy equivalence.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,sorted(added),flush=True)
