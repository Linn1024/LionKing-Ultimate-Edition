"""Record the usable bulk source preset and its focused real-window evidence."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
notice='''CURRENT403: Public398 adds an Available MD draft preset. SDL Resources has
MD/F7; ImGui has Available MD. Ready supported leaves inherit an MD root;
unavailable leaves explicitly use SNES. Branch/leaf overrides remain useful.
Apply persists and restarts through the ordinary coordinator. Upgrade preserves
all installed data/settings. Read docs/available-md-preset.md (project root).
398 replaces only resources/host/menu objects; 401 PASS9 actual SDL interaction
and inspected preset/override/gameplay windows;402 installed publication passes.
399/400 harnesses accidentally used menu screenshot auto-exit and never reached
interaction;401 removes that flag. ImGui button compiled, no separate GL claim.
No guest/audio/artwork/save/data/schema changes or unrelated route/full suites.
Public398 SHA256:
be29819ad0891814b99350e755f4c608c7b8536c465aa9531d8fc12876d90b74.
The old1.55s figure was title loading, not a proven hyena-wait defect; later
title-bank work already reduced it. No speculative timing fix was made.
First-level fidelity goal stays OPEN. Continue visible gameplay/resource gaps
and practical walkthrough work; no instrument-only transition refinements.
Earlier entries below are historical and may be superseded.

'''
for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/launchers.md','README.md'):
    path=ROOT/name;text=path.read_text(encoding='utf-8')
    if not text.startswith('CURRENT403:'):path.write_text(notice+text,encoding='utf-8')
path=ROOT/'engine/docs/devlog.md';text=path.read_text(encoding='utf-8')
if '## Available MD draft preset397..403' not in text:path.write_text(text+'\n\n## Available MD draft preset397..403\n\n'+notice+'See root docs/available-md-preset.md. Framework submodules untouched.\n',encoding='utf-8')
reports=[ROOT/name for name in ('build/pride398/build-report.json','build/pride401-ui/report.json','build/pride402-publication/report.json','dist/installed-preview398/package-report.json')]
for p in reports:bound(p)
paths=[Path(__file__),*reports,*[ROOT/name for name in ('docs/available-md-preset.md','docs/HANDOFF.md','docs/pride-lands-status.md','docs/launchers.md','README.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1')]]
out=ROOT/'build/pride403-bindings';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='PASS',full_first_level_complete=False,scope='Public398 usable available-source preset, actual SDL Apply/override/restart and preservation; goal open.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('Recorded public398 and checked current evidence bindings.')
