"""Bind the published second-level background and current handoff identities."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
paths=[ROOT/'build'/p/'report.json' for p in ('cant-wait363','cant-wait364','cant-wait365-ride','cant-wait366-publication')]
paths += [ROOT/'build/cant-wait362/build-report.json',ROOT/'dist/installed-preview362/package-report.json']
results={p.relative_to(ROOT).as_posix():bound(p)['result'] for p in paths}
assert all(v=='PASS' for k,v in results.items() if k.endswith('/report.json'))
for name in ('docs/HANDOFF.md','docs/cant-wait-live-background.md','docs/cant-wait-renderer.md','docs/next-levels-status.md','docs/pride-lands-status.md','docs/background-audit.md','docs/launchers.md','README.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1'):paths.append(ROOT/name)
paths.append(Path(__file__))
out=ROOT/'build/cant-wait368-bindings';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='PASS',published=True,full_first_level_complete=False,results=results,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print(results)
