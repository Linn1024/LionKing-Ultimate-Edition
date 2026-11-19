"""Preserve shared actor hooks before extending verified Exile ownership."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next742-audio-baseline';out.mkdir();rows={}
for name in ('engine/runner/tlk_lizard_audio.c','engine/runner/tlk_leaves.c'):
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('next736-data-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('next742-audio-baseline')"))
