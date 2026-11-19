"""Preserve the first next-level build before visible backdrop/coverage corrections."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next746-correction-baseline';out.mkdir();rows={}
for file in ('tlk_wide.c','tlk_md_sprites.c','tlk_resources.c','tlk_audio.c'):
 name='engine/runner/'+file;p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('next744-sprite-map-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('next746-correction-baseline')"))
