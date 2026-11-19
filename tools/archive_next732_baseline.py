"""Preserve current720 sources before fourth/fifth-level adapters."""
import json,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next732-baseline';out.mkdir();rows={}
names=['engine/runner/'+x for x in ('tlk_md_assets.c','tlk_md_assets.h','tlk_md_assets_cache.inc','tlk_wide.c','tlk_wide.h','tlk_md_sprites.c','tlk_md_sprites.h','tlk_md_sprite_format.inc','tlk_resources.c','tlk_audio.c','tlk_roar.c')]
names += ['tools/pride_sprite_catalog.py','tools/graveyard_sprite_catalog.py','docs/HANDOFF.md','docs/background-audit.md','docs/next-levels-status.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1','game-data/install.json']
for name in names:
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('graveyard722-publication-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('next732-baseline')"));print('ARCHIVED',len(rows))
