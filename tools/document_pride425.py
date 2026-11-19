"""Record the published per-component HUD feature and bind its focused evidence."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
p=ROOT/'docs/HANDOFF.md';s=p.read_text()
s=s.replace('Current416, 2026-11-10. The first-level fidelity goal remains OPEN. Public398 is\nthe current Windows player; no game/runtime change was made in404..416.', 'Current425, 2026-11-10. The first-level fidelity goal remains OPEN. Public418 is\nthe current Windows player; its resources/compositor change separates HUD artwork\nchoices. No game/runtime change was made in404..416.')
s=s.replace('dist/installed-preview398/LionKing.exe','dist/installed-preview418/LionKing.exe').replace('be29819ad0891814b99350e755f4c608c7b8536c465aa9531d8fc12876d90b74','57f409d6ea3a4b67d4d4421deb1991c0a578dc31377f8eea7a1fa077760fd69a')
s=s.replace('| Available MD preset398 |','| Independent HUD418 | Separate roar, health and lives artwork under the existing Meters and lives group; live Apply. [Details](pride-independent-hud.md);421 isolated settled-play output/guest/audio,423 actual SDL interaction/windows,424 installed publication. |\n| Available MD preset398 |')
s=s.replace('Latest source archive415 preserves the410 handoff/status; current aggregate\nis `build/pride416-bindings/report.json`. All411/414 runs are terminal.', 'Latest source archive417 preserves the416 handoff/status and preceding HUD\nsources; current HUD aggregate is `build/pride425-bindings/report.json`.\nAll411/414 and419..424 runs are terminal.')
p.write_text(s)
p=ROOT/'docs/pride-lands-status.md';s=p.read_text().replace('Current416, 2026-11-10. Public398','Current425, 2026-11-10. Public418')
s=s.replace('| Windows installed player |402 installed candidate/publication;401 real UI and408 actual arena window | Usable published398;', '| Windows installed player |424 installed candidate/publication;423 real HUD UI/window, inherited401/408 preset/arena | Usable published418;')
s=s.replace('| Source tree and switching |401 preset draft,', '| Source tree and switching |423 independent roar/health/lives live Apply;421 isolated HUD output;401 preset draft,')
p.write_text(s)
p=ROOT/'engine/docs/devlog.md';s=p.read_text();s+='\n\n## Independent Pride HUD artwork417..425\n\nPublic418 separates roar/health/lives under the existing whole-HUD source group.\nOnly resources/compositor objects change; existing profiles inherit all three,\nshared palette stays independent. Prepared assets, guest, audio and save code\nunchanged; hyena OAM ownership repair retained.421 PASS13 settled-play isolation,\nold whole/native pictures and guest/audio preservation;423 PASS6 actual SDL\nchild edit/live Apply/persistence and inspected real Windows clients.420/422\nharnesses failed to close ordinary settings menus; no product changes followed.\n424 installs/publishes through existing launchers with all data/settings exact.\nNo unrelated suites or transition-frame fixes. See root docs/pride-independent-hud.md.\nFirst-level fidelity goal remains OPEN.\n';p.write_text(s)
reports=[ROOT/('build/'+name+'/report.json') for name in ('pride421-hud-play','pride423-hud-ui','pride424-publication')]
for p in reports:assert bound(p)['result']=='PASS'
build=ROOT/'build/pride418/build-report.json';assert bound(build)['result']=='BUILT'
out=ROOT/'build/pride425-bindings';out.mkdir(exist_ok=True)
paths=[Path(__file__),build,*reports,*[ROOT/name for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-independent-hud.md','engine/docs/devlog.md','engine/runner/tlk_resources.c','engine/runner/tlk_resources.h','engine/runner/tlk_wide.c','tools/pride_arena_history.py','scripts/RunInstalledPreview.ps1')]]
(out/'report.json').write_text(json.dumps(dict(result='PROGRESS_GOAL_OPEN',published=True,first_level_complete=False,scope='Independent first-level HUD artwork published; focused rendered/guest/audio/UI/installed evidence only. Broader original gameplay fidelity remains scoped.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PROGRESS_GOAL_OPEN',flush=True)
