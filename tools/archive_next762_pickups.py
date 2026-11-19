"""Preserve the death-qualified build before enabling the three observed Exile pickup owners."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next762-pickup-baseline';out.mkdir();rows={}
for name in ('engine/runner/tlk_wide.c','engine/runner/tlk_md_sprites.c','engine/runner/tlk_resources.c'):
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('next758-availability-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('next762-pickup-baseline')"))
