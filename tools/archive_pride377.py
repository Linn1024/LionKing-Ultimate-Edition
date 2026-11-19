"""Preserve public372 sources before install-time contact/palette preparation."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride377-baseline';out.mkdir();records={}
for name in ('engine/runner/tlk_contact_map.c','engine/runner/tlk_contact_map.h','engine/runner/tlk_md_assets.c','engine/runner/tlk_md_assets_cache.inc','engine/runner/tlk_resources.c','engine/runner/sdl_main.c','engine/runner/headless_main.c','engine/tools/prepare_scene_assets.c','engine/cmake/TlkSceneAssets.cmake','scripts/Setup.ps1','scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-lands-status.md','docs/background-audit.md','docs/launchers.md','engine/docs/devlog.md','README.md'):
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('cant-wait369-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride377-baseline')"))
