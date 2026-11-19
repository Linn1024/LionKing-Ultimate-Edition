"""Preserve public382 before bundled gameplay-table preparation."""
import json,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride388-baseline';out.mkdir();records={}
names=['engine/runner/tlk_'+part+suffix for part in ('start_data','reactivation_data','hitbox_data','roar_data') for suffix in ('.c','.h')]
names+=['engine/runner/tlk_md_sprite_format.inc','engine/runner/tlk_md_sprite_prepare.c','engine/runner/tlk_md_sprite_assets.inc','engine/runner/tlk_resources.c','engine/cmake/TlkSpriteAssets.cmake','engine/CMakeLists.txt','scripts/Setup.ps1','scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-lands-status.md','docs/launchers.md','engine/docs/devlog.md','README.md']
for name in names:
    p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride377-baseline')";assert s.count(anchor)==1;p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride388-baseline')"))
