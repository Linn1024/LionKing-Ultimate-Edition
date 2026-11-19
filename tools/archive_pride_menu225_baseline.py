"""Preserve exact bound sources before normal menu resource integration."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride-menu225-baseline';out.mkdir();records={}
paths=['engine/runner/tlk_resources.c','engine/cmake/TlkPrideFinalPlayer.cmake','tools/pride_arena_history.py',
       'docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-final-menu-native-continue.md',
       'docs/pride-final-menu-native-timing.md','docs/background-audit.md','engine/docs/devlog.md']
paths += ['engine/runner/pride/final/'+name for name in ('pride_final_host.c','pride_final_menu.inc',
    'pride_final_runtime.inc','pride_final_present.inc','pride_final_save.inc')]
for name in paths:
    p=ROOT/name;copy=out/name;copy.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,copy)
    records[name]=dict(sha256=digest(p),archive=copy.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
print('ARCHIVED',len(records),flush=True)
