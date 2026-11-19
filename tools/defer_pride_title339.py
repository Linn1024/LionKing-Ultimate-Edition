"""Retain the one-frame prototype without including it in ordinary builds."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride-title339-deferred';out.mkdir();records={}
for name in ('engine/runner/pride/final/pride_final_runtime.inc','engine/runner/pride/final/pride_final_title_dma.inc','engine/recomp/pride_final_hooks.json','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-lands-status.md','engine/docs/devlog.md'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(result='DEFERRED',published=False,historical_sources=records,reason='User prioritizes differences visible during ordinary play; do not pursue the one-frame title preparation change.'),indent=2)+'\n')
for name in ('engine/runner/pride/final/pride_final_runtime.inc','engine/recomp/pride_final_hooks.json'):
    shutil.copy2(ROOT/'build/pride-title336-baseline'/name,ROOT/name)
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride-title336-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-title339-deferred')"))
print('Deferred: ordinary sources restored; public327 unchanged')
