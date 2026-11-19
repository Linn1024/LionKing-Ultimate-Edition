"""Qualify existing real UI captures using the draft column for pending choices."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

source=ROOT/'build/pride-hyena-probe103/windows-ui/report.json';r=bound(source)
assert r['result']=='FAIL' and [k for k,v in r['checks'].items() if not v]==['md_leaf_available','snes_leaf_available']
out=ROOT/'build/pride-hyena-probe103/windows-ui-qualification104';out.mkdir()
checks={k:v for k,v in r['checks'].items() if not k.endswith('_leaf_available')}
node='gameplay.levels.pride_lands.hyena_probe_height'
for label,choice in [('md',2),('snes',1)]:
    row=next(c for c in r['snapshots'][label+'-draft']['choices'] if c[0]==node)
    checks[label+'_draft_explicit_and_resolved_choice']=row[1]==row[3]==choice
    checks[label+'_active_after_restart']=next(c[-1] for c in r['snapshots'][label+'-after']['choices'] if c[0]==node)==choice
checks['original_failed_checks_were_old_active_column']=all(next(c[-1] for c in r['snapshots'][label+'-draft']['choices'] if c[0]==node)!=choice for label,choice in [('md',2),('snes',1)])
paths=[Path(__file__),source]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
    actual_captures_inspected=['md-draft.png','md-gameplay.png','snes-draft.png','snes-gameplay.png'],
    correction='Original verifier read active resolved column during a pending draft; correct pending columns are1 and3. Both restarts, source persistence, pause/audio freeze, difficulty, other choices and clean exit passed originally. No player or recorded output change.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('UI',sum(checks.values()),'/',len(checks),flush=True)
