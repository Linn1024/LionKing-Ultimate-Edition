"""Preserve existing source identities before recording the countdown proof."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

proof=ROOT/'build/pride-hyena-countdown133/report.json'
r=bound(proof);assert r['result']=='PASS' and all(r['checks'].values())
base=ROOT/'build/pride-hyena-countdown133-baseline';base.mkdir();rows={}
for name in ('docs/HANDOFF.md','docs/pride-hyena-entrance.md','engine/docs/devlog.md','tools/pride_arena_history.py'):
    p=ROOT/name;q=base/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(base/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
history=ROOT/'tools/pride_arena_history.py';s=history.read_text();anchor="    folders.append('pride-resource-tree118-baseline')"
assert s.count(anchor)==1
history.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-hyena-countdown133-baseline')"))
handoff=ROOT/'docs/HANDOFF.md';s=handoff.read_text();anchor='# Lion King PC development handoff\n'
assert s.startswith(anchor)
note='''
FOLLOW-UP133: PROGRESS. Extended unlinked entrance operand adapter proof from
isolated window output to complete original entrance countdown decisions.
build/pride-hyena-countdown133/report.json TERMINAL PASS5:251 recorded natural
camera/player/actor coordinate sets x positive timers1..60 =15,060 fixtures.
All native decisions match independent original113; selected decisions match
unmodified original MD19B5EA slice, including180 width-dependent decisions.
15,060 actual adapter adjustments; actor/timer/CPU preservation checks inherited
from132 and enforced inside each full helper call. Slice stops before actual
jump/music callees; native audio wait fixed0. Not a full live trajectory, source
switch, audible onset or new selectable capability claim. Current118 untouched.

Only live job remains118 native75 session52074, last terminal output through
l11_right MATCH; live children confirmed in l12_random-lle and l12_right-aot.
Poll SAME handle. No publication yet, public86. After terminalPASS302/all75 use
publisher123 -> CMD124 terminal first -> OS125/Mixed126 ->four OS inspections ->
public docs -> binder127 LAST. Keep118 rather than superseding it. Unlinked
entrance module integration follows release. New research133 sources are bound;
archive before editing. Original header/source dependencies also bound by132.
'''
handoff.write_text(anchor+note+'\n'+s[len(anchor):])
doc=ROOT/'docs/pride-hyena-entrance.md'
with doc.open('a') as f:f.write('''

The133 decision-slice proof now executes the maintained adapter inside complete
original entrance wait/jump decisions, including the full window helper. All251
recorded waiting coordinate sets are checked at positive timers1..60 (15,060
fixtures). Native results match the independent unmodified original113 slice;
selected results match unmodified original MD19B5EA decisions at the same inputs.
There are180 source-dependent countdown decisions and15,060 adapter adjustments.
The native comparison translates coordinates to113's fixed actor location while
preserving actor/camera geometry and player-relative predicates. Actual adapter
calls use the observed relative frame, real page2 stack and C14480 caller.

`build/pride-hyena-countdown133/report.json` passes five checks. Native audio wait
is fixed0 and both slices stop before the actual jump/music callees. Positive
timer fixtures establish decision behavior; they do not establish a whole live
countdown trajectory, audible timing, interruptions or source-switch lifecycle.
Synthetic timer0 behavior remains outside the selectable feature. Current118
binary and all323 linked inputs remain unchanged; no new player option enabled.
''')
with (ROOT/'engine/docs/devlog.md').open('a') as f:f.write('''

## Original entrance decision proof133 (2026-11-10)

The unlinked native entrance window adapter now executes in the complete original
SNES wait/jump decision slice with observed caller/frame guards. At251 original
recorded coordinate sets x positive timers1..60, all15,060 native decisions match
the independent original113 slice and selected decisions match unmodified MD
19B5EA.180 source-dependent decisions;15,060 actual operand adjustments. PASS5.
Each adapter invocation checks RAM and CPU preservation except the intended A
operand. Native audio wait fixed0; stop before actual jump/music callees. No
full live countdown/menu/switch/audio-onset claim or production capability yet.
No current118 binary/link changes, pending native75 is still the same live run.
''')
build=bound(ROOT/'build/pride-resource-tree118/build-report.json')
assert all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
assert digest(ROOT/'build/pride-resource-tree118/player.exe')==build['binary_sha256']
print('Recorded133 proof; current118 binary and all323 inputs unchanged',flush=True)
