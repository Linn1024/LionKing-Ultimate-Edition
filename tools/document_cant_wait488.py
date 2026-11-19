"""Close the practical second-level milestone using existing focused evidence."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
names=('cant-wait462-rhino','cant-wait463-ui','cant-wait464-setup','cant-wait467-publication','cant-wait477-tail-qualified','cant-wait480-ui','cant-wait483-hud','cant-wait485-route','cant-wait487-publication')
reports=[ROOT/'build'/name/'report.json' for name in names]
for p in reports:assert bound(p)['result']=='PASS'
p=ROOT/'docs/HANDOFF.md';s=p.read_text();start=s.index('Current468,');end=s.index('\nRead [current first-level status]')
s=s[:start]+'''Current488, 2026-11-10. The first- and second-level practical playable milestones
are COMPLETE; development through the ending remains unfinished. Public482 adds
live rhino tail colors and shared second-level HUD artwork, retaining rhino head,
monkey/ostrich, scenery and music choices. The full second-level route reaches
Elephant Graveyard. Read [the second-level review](cant-wait-delivery-review.md)
for evidence, native sound/gameplay limits and the practical stopping rule.

- Player: `dist/installed-preview482/LionKing.exe`
- SHA256: `5d873d4ba0bc27ce5a6308c3e79987b9657c93927dde00ce00bf4265ce095e3d`
- Launcher: `scripts/RunInstalledPreview.ps1`, used by existing root Play CMDs.
- Default data: `game-data/install.json`, existing scene-v2/sprite-v2 packages.
- Settings, preparation helper, old assets and builds are preserved.
''' + s[end:]
s=s.replace('| Can\'t Wait rhino art460 |', '| Can\'t Wait delivery482 | Full direct-selected walkthrough485 into Elephant Graveyard, live tail palette480 and shared HUD483, installed publication487. [Review](cant-wait-delivery-review.md). |\n| Can\'t Wait rhino art460 |')
start=s.index("Proceed through every remaining level and the ending. Can't Wait now has")
end=s.index('\nRoutine checks MUST',start)
s=s[:start]+'''Can't Wait's practical milestone is complete. Next is Elephant Graveyard;
reuse existing scenery/cub/music adapters and identify concrete remaining scene
or actor gaps before editing. Read [remaining-level plan](remaining-levels-plan.md)
as the broader roadmap, with this current status superseding its dated animal
work list. The RAM-backed frames previously called giraffe heads were actually
the rhino tail: descriptorC58C08, 11 shared drawings, separate head descriptor
C58C14. Giraffe/large rhino bodies are scene art. Do not repeat that mistaken
actor investigation. Second-level sounds/gameplay retain native behavior;
scope limitations are recorded in the delivery review.
''' +s[end:]
s=s.replace('Rhino462/463 use direct\nlevel2 select and a short approach after loading, with no level1 replay.', 'Rhino462/463 use direct\nlevel2 select and a short approach after loading, with no level1 replay.485 now\nprovides a current482 entry save and completed sliced continuation:4235 polls\nbefore level2, actual scene/health guards, no external tape during level select.')
s=s.replace('`build/cant-wait468-bindings/report.json`.457/465 preserve prior source/install\nidentities. All retained runs are terminal; public460 is selected.', '`build/cant-wait488-delivery/report.json`.457/465/472/478/486 preserve prior\nsource/install identities. All retained runs are terminal; public482 is selected.')
s=s.replace('The first-level review is complete. Create/resume the explicitly requested next\ngoal for every remaining level through the ending.', 'The first- and second-level practical reviews are complete. The broader\nremaining-level roadmap continues with Elephant Graveyard.')
p.write_text(s)
p=ROOT/'docs/next-levels-status.md';p.write_text('''CURRENT488: Public482 completes the practical second-level walkthrough into
Elephant Graveyard. Rhino tail colors and shared roar/health/lives HUD choices
are live; previous resources retained.485 PASS7 complete direct-selected route
from current save;477 tail,480 UI,483 HUD and487 installed publication pass.
Read root docs/cant-wait-delivery-review.md for supported choices and limits.
Second-level gameplay/effects remain native; universal MD parity is not claimed.
The RAM-backed presumed giraffe head was actually the rhino tail, descriptor
C58C08, 11 shared drawings. Full WRAM/init evidence corrected the owner.
Next level is Elephant Graveyard. Earlier entries below are dated history.

'''+p.read_text())
p=ROOT/'docs/second-level-goal.md';s=p.read_text();s=s.replace('# Second-level goal: Can\'t Wait to Be King', '# Second-level goal: Can\'t Wait to Be King\n\nStatus: practical playable milestone COMPLETE, preview482. Full direct-selected\nroute485 reaches Elephant Graveyard. See [delivery review](cant-wait-delivery-review.md)\nfor delivered choices, evidence and retained native gameplay/sound limits.\nThe original goal and strategy below are preserved as the task record.')
p.write_text(s)
p=ROOT/'docs/cant-wait-rhino-art.md';s=p.read_text();start=s.index('Next is giraffe head ownership/art.');s=s[:start]+'''Update488: full7E/7F decoding and original initialization identified those
RAM-backed frames as the rhino tail, not a separate giraffe head. Its11 anchored
drawings are shared; preview482 adds an independent live Tail > Palette choice.
Head leaves are labelled Head artwork / Head palette. Giraffe and large rhino
bodies belong to scene foreground art. The full second-level route485 now reaches
Elephant Graveyard. See [delivery review](cant-wait-delivery-review.md) for tail,
HUD, current save/load, publication and native gameplay/sound limits.
''';p.write_text(s)
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''

## Can't Wait practical completion469..488

Public482 adds guarded independent rhino tail colors and shared roar/health/lives
HUD artwork in actual level1/descriptor3B9. Full WRAM/init evidence471 identifies
11 shared tail drawings, C58C08; previous giraffe-head assumption corrected.
Scene foreground owns giraffe/large rhino bodies. Tail actual palette bank1,
physical draw/actor binding and native palette fingerprint protect other owners.
HUD uses shared live sprite palette0, not raw scene table0.477 qualifies retained
474 images with corrected bank1 mask,480 actual live UI,483 isolated HUD changes
and guest preservation. No new assets/state/gameplay/audio changes for these.
485 direct-select/current cold save continuation completes puzzles/ride into
Elephant Graveyard, health4/spares3, MD music commands/output and Windows views.
484 external polled tape overrode frontend select; harness failure preserved.
487 installed publication preserves data/settings. No level1 replay, repeated
broad gate or compatibility work. Read root docs/cant-wait-delivery-review.md;
native second-level gameplay/effects and unsupported MD leaves are explicit.
''')
paths=[Path(__file__),*reports,*[ROOT/name for name in ('docs/HANDOFF.md','docs/next-levels-status.md','docs/second-level-goal.md','docs/cant-wait-rhino-art.md','docs/cant-wait-delivery-review.md','engine/docs/devlog.md','tools/pride_arena_history.py','scripts/RunInstalledPreview.ps1')]]
exe=ROOT/'dist/installed-preview482/LionKing.exe';assert digest(exe)=='5d873d4ba0bc27ce5a6308c3e79987b9657c93927dde00ce00bf4265ce095e3d'
out=ROOT/'build/cant-wait488-delivery';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='PASS',practical_second_level_complete=True,universal_md_parity=False,published=True,checks=dict(full_level_to_graveyard=True,current_cold_save_load=True,focused_resource_checks=True,actual_windows_inspected=True,installed_publication=True,native_limits_recorded=True),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},binary_sha256=digest(exe)),indent=2)+'\n')
print('SECOND_LEVEL_PRACTICAL_MILESTONE_COMPLETE; public482; next Elephant Graveyard',flush=True)
