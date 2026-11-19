"""Freeze qualified animal cues before adding silent-native animation cues and shared pickups."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/cant-wait564-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_audio.c','engine/runner/tlk_audio.h','engine/runner/tlk_roar.c','engine/runner/tlk_resources.c','tools/pride_arena_history.py','docs/cant-wait-sound-gameplay-goal.md','docs/HANDOFF.md'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('cant-wait559-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('cant-wait564-baseline')"))
