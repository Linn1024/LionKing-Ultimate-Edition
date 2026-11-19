"""Preserve the completed milestone and record the active third-level goal."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
review=ROOT/'build/cant-wait488-delivery/report.json';assert bound(review)['result']=='PASS'
out=ROOT/'build/graveyard489-baseline';out.mkdir();records={}
for name in ('docs/HANDOFF.md','docs/next-levels-status.md','tools/pride_arena_history.py'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('cant-wait486-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard489-baseline')"))
p=ROOT/'docs/HANDOFF.md';s=p.read_text().replace('Current488,','Current489,',1);s=s.replace('are COMPLETE; development through the ending remains unfinished.', 'are COMPLETE; the Elephant Graveyard goal is ACTIVE. Read\n[the third-level goal](graveyard-goal.md); development through the ending remains\nunfinished.',1);p.write_text(s)
p=ROOT/'docs/next-levels-status.md';p.write_text('''CURRENT489: Elephant Graveyard goal ACTIVE, starting from public482. Read
root docs/graveyard-goal.md and HANDOFF.md. Reuse existing Graveyard scenery,
cub artwork and MD music; inventory concrete HUD/enemy/audio gaps using direct
third-level selection/current checkpoints. No earlier-level replay or tiny
instrument-only fidelity work. Second-level practical milestone remains closed.

'''+p.read_text())
print('THIRD_LEVEL_GOAL_ACTIVE; public482 retained',flush=True)
