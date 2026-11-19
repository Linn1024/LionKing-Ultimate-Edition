"""Freeze additional coordinator sources before integrating new level gameplay observers."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard618-integration-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_audio.c','engine/cmake/TlkPrideFinalPlayer.cmake','tools/pride_arena_history.py'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('graveyard617-gameplay-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard618-integration-baseline')"))
