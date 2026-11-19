"""Preserve the completed combined-route build before the final rock-sound/color fixes."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next753-final-baseline';out.mkdir();rows={}
for name in ('engine/runner/tlk_audio.c','engine/runner/tlk_resources.c','engine/runner/tlk_wide.c','engine/cmake/TlkPrideFinalPlayer.cmake'):
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('next750-performance-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('next753-final-baseline')"))
