"""Record the published second-level animal choices and checkpoint-first workflow."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
names=('cant-wait441-monkeys','cant-wait442-ui','cant-wait449-ostrich','cant-wait450-ui','cant-wait451-publication','cant-wait452-checkpoint')
reports=[ROOT/'build'/name/'report.json' for name in names]
for p in reports:assert bound(p)['result'] in ('PASS','READY')
p=ROOT/'docs/HANDOFF.md';s=p.read_text().replace('Current434,','Current454,').replace('remaining-level development is next. Public418 is\nthe current Windows player; its resources/compositor change separates HUD artwork\nchoices. No game/runtime change was made in404..416.', 'remaining-level development is ACTIVE. Public448 is\nthe current Windows player; it adds independent monkey and ostrich colors in\nCan\'t Wait to Be King. Existing scenery, cub art, audio and game logic are retained.')
s=s.replace('dist/installed-preview418/LionKing.exe','dist/installed-preview448/LionKing.exe').replace('57f409d6ea3a4b67d4d4421deb1991c0a578dc31377f8eea7a1fa077760fd69a','72fb01357e0f491032104b3043ad04a5a7e51dc573fea7c510efae8d00e89d13')
s=s.replace('| Independent HUD418 |',"| Can't Wait animal colors448 | Independent live monkey/ostrich palette choices;29/12 verified shared frame pairs and current prepared scene colors. [Details](cant-wait-animal-palettes.md);441/449 focused outputs,442/450 actual UI/windows,451 publication. |\n| Independent HUD418 |")
s=s.replace("Proceed through every remaining level and the ending, starting with Can't Wait\nto Be King's animal artwork/ownership.", "Proceed through every remaining level and the ending. Can't Wait now has\nreviewed monkey/ostrich color choices; next address giraffe/rhino actor art.")
s=s.replace('and the scene-specific docs.\n', 'and the scene-specific docs.\n\nRoutine checks MUST start with level select or a current checkpoint. The user\nexplicitly objected to replaying level1 for each second-level check. Reuse\n`build/cant-wait452-checkpoint/report.json`: current448 ride at7000,6329 consumed\npolls, verified direct continuation and sliced tail. Do not replay the whole\nprefix for each source variant. Check build/source suitability before reuse;\nno old-development-save compatibility work is required.\n',1)
s=s.replace('All retained runs are terminal. Public418 is unchanged.', 'Sources438/446 preserve the animal changes. Current second-level aggregate is\n`build/cant-wait454-bindings/report.json`. All retained runs are terminal; public448\nis selected. First-level completion review434 remains valid as its dated milestone.')
p.write_text(s)
p=ROOT/'docs/next-levels-status.md';p.write_text('''CURRENT454: Public448 adds live, independent monkey and ostrich palette choices
in Can't Wait to Be King.29/12 reviewed shared frame pairs retain native common
artwork; existing prepared/live scene colors supply MD palettes. Focused isolated
output, guest, real SDL/Windows interaction and installed publication pass.
Read docs/cant-wait-animal-palettes.md (project root). Giraffe/rhino actor art and
remaining second-level coverage are still open. Use direct level select/current
checkpoint for routine checks: build/cant-wait452-checkpoint/report.json supplies
a verified current448 ride save and correctly sliced remaining input. Replaying
the first level for every source variant is explicitly rejected by the user.
Earlier notes below preserve their historical scope.

'''+p.read_text())
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''\n\n## Can't Wait animal colors435..454\n\nPublished448 adds independent MD monkey/ostrich palettes using existing prepared\nscene colors and live transition controller.29/12 exact anchored/indexed frame\npairs keep common native artwork. Pose, physical draw/actor, descriptor, bank and\noriginal native palette fingerprints guard colors; unknown/flashes stay native.\nOnly resources/compositor change, no new assets/save schema/behavior/audio.\n441/449 PASS6 isolated output and native/guest preservation;442/450 PASS5 actual\nSDL live Apply/persistence and inspected real Windows views.451 installed\npublication preserves data/settings. User objects to repeated level1 approaches: \n452 now creates one current448 ride checkpoint at7000,6329 consumed polls and\nverified direct7008 continuation, with correctly sliced polled tail. Use level\nselect/checkpoints for future routine checks; no old-save compatibility work.\nNo unrelated native75/All Bugs matrices. Second level remains ongoing.\nSee root docs/cant-wait-animal-palettes.md.\n''')
paths=[Path(__file__),*reports,*[ROOT/name for name in ('docs/HANDOFF.md','docs/next-levels-status.md','docs/cant-wait-animal-palettes.md','engine/docs/devlog.md','engine/runner/tlk_resources.c','engine/runner/tlk_wide.c','engine/runner/tlk_cw_monkey_metadata.h','engine/runner/tlk_cw_ostrich_metadata.h','scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py')]]
out=ROOT/'build/cant-wait454-bindings';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='SECOND_LEVEL_PROGRESS',second_level_complete=False,published=True,checkpoint_workflow=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('SECOND_LEVEL_PROGRESS; public448; checkpoint READY',flush=True)
