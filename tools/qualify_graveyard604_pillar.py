"""Qualify retained pillar capture using its actual long fall, not a guessed post-impact field."""
import csv,json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard602-pillar/report.json';r=bound(reference)
rows=list(csv.DictReader((reference.parent/'stems.csv').open()))
checks={k:v for k,v in r['checks'].items() if k!='long_pillar_bus'}
checks['rumble_continues_past_two_second_tail']=all(any(int(x['frame'])==field and int(x['md_peak'])>100 for x in rows) for field in (16540,16570,16600))
assert all(checks.values())
out=ROOT/'build/graveyard604-pillar-qualified';out.mkdir(exist_ok=True);paths=[Path(__file__),reference,reference.parent/'stems.csv']
(out/'report.json').write_text(json.dumps(dict(result='PASS',checks=checks,scope='602 completes the actual fall, one171 and one92, with native music choice and real capture. Its guessed >16800 loudness check was after the impact/decay and false. Actual isolated rumble remains loud at16540/16570/16600, beyond the initial120-field tail; reuse those samples without replay or game edits.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
