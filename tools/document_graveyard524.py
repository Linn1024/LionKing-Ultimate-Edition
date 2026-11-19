"""Record installed third-level progress and preserve reusable current research/route fixtures."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reports=[ROOT/'build'/name/'report.json' for name in ('graveyard494-hud','graveyard504-hyenas','graveyard512-ui','graveyard514-publication','graveyard516-route')]
for p in reports:assert bound(p)['result']=='PASS'
p=ROOT/'docs/HANDOFF.md';s=p.read_text().replace('Current489,','Current524,',1)
start=s.index('unfinished. Public482 adds');end=s.index('\nRead [current first-level status]',start)
s=s[:start]+'''unfinished. Public503 adds Graveyard shared HUD and independent hyena artwork/
scene-specific colors. Full current walkthrough516 reaches a visible Stampede.
The Graveyard goal remains ACTIVE: vultures and bone hazards are next. Read
[current Graveyard resources/fixtures](graveyard-resources.md).

- Player: `dist/installed-preview503/LionKing.exe`
- SHA256: `c703ae76d0ca8e91e7ea985aeb7cd86cd7233076eeb579eba49a458084caac11`
- Launcher: `scripts/RunInstalledPreview.ps1`; root Play CMDs use it.
- Direct third level: `Play Elephant Graveyard Mix.cmd`.
- Existing scene-v2/sprite-v2 assets, helper, settings and earlier builds retained.
''' +s[end:]
s=s.replace('| Can\'t Wait delivery482 |', '| Graveyard progress503 | Shared HUD494, independent guarded hyena artwork/colors504, live UI512, installed publication514. Full route516 reaches visible Stampede. [Current resources and checkpoints](graveyard-resources.md); vulture/bone work remains active. |\n| Can\'t Wait delivery482 |')
s=s.replace("Can't Wait's practical milestone is complete. Next is Elephant Graveyard;\nreuse existing scenery/cub/music adapters and identify concrete remaining scene\nor actor gaps before editing.", "Can't Wait's practical milestone is complete. Elephant Graveyard is active;\nreuse its existing scenery/cub/music, now-shipped HUD and hyena adapters.\nNext use current vulture fixture523 for descriptorC58CD8/native palette5.\nIdentify original animation streams and bank initialization before new mappings.")
anchor='## Subsystem reading map';assert s.count(anchor)==1;s=s.replace(anchor,'''Graveyard current route entry511 has original RNG and naturally earned upgrades,
field13147,12162 consumed original polls. Use this instead of replaying earlier
levels. Full route516 and mid-level522/523 current saves are already available.
A fresh direct selection has only four health points and different carry-in
state; do not force the recorded route onto it or add old-save compatibility.
Routine vulture work should resume523 at15000 with its actual consumed suffix.
See the resource/fixture document for all setup failures and corrections.

'''+anchor)
s=s.replace('source/install identities. All retained runs are terminal; public482 is selected.', 'source/install identities. Graveyard489/491/501/513 preserve newer bound sources.\nAll retained runs are terminal; public503 is selected. Current third-level\naggregate is `build/graveyard524-bindings/report.json`.')
p.write_text(s)
p=ROOT/'docs/next-levels-status.md';p.write_text('''CURRENT524: Graveyard goal ACTIVE; public503 ships independent shared HUD
and hyena images/scene-specific colors.494/504 focused checks,512 live UI and
514 installed publication pass. Full current route516 reaches visible Stampede.
Read root docs/graveyard-resources.md. Vultures and bone hazards remain active;
use current523 vulture save15000, descriptorC58CD8/native palette5. Route511
entry13147 consumed12162 original polls and carries natural health upgrades.
No routine earlier-level replay or old-save compatibility work is needed.

'''+p.read_text())
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''

## Elephant Graveyard resource progress489..524

Public503 extends the shared HUD into owned level2/3EB and reuses reviewed hyena
pose pairs for physically bound C58C74 actors. Native bank6/flash guard retained;
Graveyard MD bank3 comes from existing prepared scene1FF24E, independently of
scenery choice. Resources/compositor/sprites/assets accessor only; no guest,
audio, package or state-schema changes.494 PASS7 isolated HUD;504 PASS9 one-field
art/palette/native controls;512 PASS5 actual paused live Apply/persistence and
inspected Windows.514 publication preserves assets/settings (only a concurrent
live recording excluded from immutable-file assertion). Current fixture511
authors natural recorded carry-in once; full route516 passes through Bug Toss
to visible Stampede. No old-save compatibility repair; malformed/mismatched
setup attempts retained. See root docs/graveyard-resources.md for checkpoints,
input slicing, tagged MD pointers and actual vulture/native palette5 evidence.
Goal active; next vultures/bone hazards. Do not repeat prior whole routes after
local art changes without a connected progression concern.
''')
paths=[Path(__file__),*reports,*[ROOT/'build'/name/'report.json' for name in ('graveyard511-checkpoint','graveyard519-wram','graveyard521-vultures','graveyard522-enemies','graveyard523-vultures')],*[ROOT/name for name in ('docs/HANDOFF.md','docs/next-levels-status.md','docs/graveyard-goal.md','docs/graveyard-resources.md','engine/docs/devlog.md','tools/pride_arena_history.py','scripts/RunInstalledPreview.ps1')]]
out=ROOT/'build/graveyard524-bindings';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='THIRD_LEVEL_PROGRESS',third_level_complete=False,published=True,current_player=503,full_route_to_stampede=True,next_work='Vulture and bone-hazard independent resource choices, using existing current checkpoints and original streams.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('THIRD_LEVEL_PROGRESS; public503; route complete; vultures/bones next',flush=True)
