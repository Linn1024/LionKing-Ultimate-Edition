"""Freeze published King level before independent Graveyard sound work."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard589-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_audio.c','engine/runner/tlk_audio.h','engine/runner/tlk_hyena_audio.c','engine/runner/tlk_hyena_audio.h','engine/runner/tlk_roar.c','engine/runner/tlk_resources.c','tools/pride_arena_history.py','docs/HANDOFF.md','docs/graveyard-goal.md','docs/graveyard-delivery-review.md','docs/graveyard-resources.md','docs/next-levels-status.md','docs/launchers.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1','engine/cmake/game-patches/zz-continue-token-behavior-resource.hunks'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('cant-wait585-delivery-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard589-baseline')"))
