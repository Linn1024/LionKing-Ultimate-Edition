"""Preserve public503 and its preparer/map identities before adding vulture assets."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard527-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_resources.c','engine/runner/tlk_wide.c','engine/runner/tlk_md_sprites.c','engine/runner/tlk_md_sprites.h','engine/generated/resources/pride_sprite_map.h','tools/pride_sprite_catalog.py','tools/pride_arena_history.py','docs/HANDOFF.md','docs/graveyard-resources.md','docs/next-levels-status.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1','game-data/install.json','dist/PrepareSpriteAssets.exe'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('graveyard513-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard527-baseline')"))
