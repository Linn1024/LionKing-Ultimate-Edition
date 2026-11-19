"""Preserve public327 before native blank-title transfer batching."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride-title336-baseline';out.mkdir();records={}
for name in ('engine/runner/pride/final/pride_final_runtime.inc','engine/recomp/pride_final_hooks.json','engine/cmake/TlkPrideFinalPlayer.cmake','tools/pride_arena_history.py','scripts/RunInstalledPreview.ps1','docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-final-title-return.md','engine/docs/devlog.md','docs/launchers.md','README.md'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride-porcupine326-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-title336-baseline')"))
