"""Preserve current release/contact documentation before recording difficulty evidence."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
assert bound(ROOT/'build/pride-contact176-bindings/report.json')['result']=='PASS'
failed=ROOT/'build/pride-porcupine181-ready-aligned';attempt=failed/'attempt-report.json';assert not attempt.exists()
attempt.write_text(json.dumps(dict(result='FAIL',reason='First Easy player process exited0. Parser expected initialized player/health at a latched UI-ready boundary; actual RAM still had health0/player0.182 uses the later real actor allocation. Raw run and full RAM retained; no guest edits.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (ROOT/'tools/capture_pride_porcupine181_ready_aligned.py',ROOT/'tools/capture_pride_porcupine177_difficulty.py')},
    artifacts_sha256={p.relative_to(failed).as_posix():digest(p) for p in failed.rglob('*') if p.is_file()}),indent=2)+'\n')
base=ROOT/'build/pride-porcupine195-baseline';base.mkdir();rows={}
for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-porcupine-contacts.md','docs/pride-porcupine-runtime.md','docs/pride-porcupine-applicability.md','engine/docs/devlog.md','tools/pride_arena_history.py'):
    p=ROOT/name;q=base/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(base/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride-contact175-baseline')";assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-porcupine195-baseline')"))
print('Archived current139/contact identities and retained181 failure',flush=True)
