"""Preserve published sound build before independent Graveyard gameplay/data choices."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard617-gameplay-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_hitboxes.c','engine/runner/tlk_hitbox_data.c','engine/runner/tlk_hitbox_data.h','engine/runner/tlk_md_sprite_format.inc','engine/runner/aot_pace.h','engine/runner/tlk_resources.c','tools/pride_hitbox_catalog.py','engine/generated/resources/pride_hitbox_map.h','tools/pride_arena_history.py','docs/HANDOFF.md','docs/graveyard-sound-delivery.md','docs/graveyard-goal.md','docs/graveyard-resources.md','docs/next-levels-status.md','docs/launchers.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('graveyard614-delivery-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard617-gameplay-baseline')"))
