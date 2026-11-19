"""Complete the practical Graveyard delivery review from qualified current sources and retained evidence."""
import json,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
names=('graveyard494-hud','graveyard504-hyenas','graveyard512-ui','graveyard516-route','graveyard531-vultures','graveyard532-ui','graveyard538-setup','graveyard539-ui','graveyard540-bones-qualified','graveyard541-publication')
reports=[ROOT/'build'/name/'report.json' for name in names]
for p in reports:assert bound(p)['result']=='PASS'
build=ROOT/'build/graveyard536/build-report.json';b=bound(build)
helper=ROOT/'build/graveyard529-helper/build-report.json';h=bound(helper)
late=ROOT/'build/graveyard544-fight/report.json';lr=bound(late);assert lr['scene']['descriptor']==0x3eb and lr['scene']['health']>0 and ('0xc58c74','0xc2ad3e',6) in [tuple(x) for x in lr['inventory']]
manifest=ROOT/'game-data/install.json';m=json.loads(manifest.read_text(encoding='utf-8-sig'))
packet=manifest.parent/m['sprite_assets']['file'];assert digest(packet)==h['cache_sha256']
package=ROOT/'dist/installed-preview536/package.json';pkg=json.loads(package.read_text());exe=package.parent/'LionKing.exe'
assert digest(exe)==b['binary_sha256']==pkg['player_sha256']=='5e408d648a8bf2b7b39898533f1d33643404f2779411927ef2e0ab395412efc5'
assert pkg['required_sprite_policy_sha256']==packet.read_bytes()[88:120].hex() and m['sprite_assets']['version']==2
assert digest(ROOT/'dist/PrepareSpriteAssets.exe')==h['binary_sha256']
assert 'dist/installed-preview536' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
p=ROOT/'docs/HANDOFF.md';s=p.read_text();a=s.index('Current524,');z=s.index('\nRead [current first-level status]',a)
s=s[:a]+'''Current546, 2026-11-10. The first three practical playable milestones are
COMPLETE. Development through the ending remains unfinished; next is The
Stampede. Read [Graveyard delivery review](graveyard-delivery-review.md) for
implemented choices, complete route evidence and explicit native limits.

- Player: `dist/installed-preview536/LionKing.exe`
- SHA256: `5e408d648a8bf2b7b39898533f1d33643404f2779411927ef2e0ab395412efc5`
- Launcher: `scripts/RunInstalledPreview.ps1`; existing root Play CMDs use it.
- Direct third level: `Play Elephant Graveyard Mix.cmd`.
- Native Setup/default sprite-v2 assets upgraded for46 vulture images/native
  bank5; existing settings, other packages, old assets and builds retained.
''' +s[z:]
s=s.replace('| Graveyard progress503 |', '| Graveyard delivery536 | Independent46-frame vulture artwork/colors and four bone-platform colors, shared HUD and hyenas.531/540 focused controls,532/539 actual UI,538/541 native Setup/publication, full route516 and current final fight544. [Review](graveyard-delivery-review.md). |\n| Graveyard progress503 (history) |')
a=s.index("Can't Wait's practical milestone is complete. Elephant Graveyard is active;");z=s.index(' Read [remaining-level plan]',a)
s=s[:a]+'''Can't Wait and Elephant Graveyard practical milestones are complete. Next is
The Stampede: inspect its actual special-scene rendering and reuse existing MD
music. Resource viewport currently stays native256 there; do not assume this
scene has Graveyard planes, scroll bands or ordinary world margins. The current
Graveyard resources and source limits are in its delivery review.''' +s[z:]
s=s.replace('Current third-level\naggregate is `build/graveyard524-bindings/report.json`.', 'Current third-level\ndelivery aggregate is `build/graveyard546-delivery/report.json`.527/535/545\npreserve the preceding renderer, generator, helper, manifest and goal docs.')
s=s.replace('All retained runs are terminal; public503 is selected.', 'All retained runs are terminal; public536 is selected.')
s=s.replace('The first- and second-level practical reviews are complete. The broader\nremaining-level roadmap continues with Elephant Graveyard.', 'The first three practical reviews are complete. The broader remaining-level\nroadmap continues with The Stampede.')
p.write_text(s)
p=ROOT/'docs/graveyard-goal.md';s=p.read_text().replace('Status: ACTIVE, 2026-11-10. Continue from preview482 and the completed practical', 'Status: practical milestone COMPLETE, preview536, 2026-11-10. See\n[the delivery review](graveyard-delivery-review.md) for requirements, actual\nevidence and retained native behavior. The original goal/strategy below is\npreserved as the task record. Continue from preview482 and the completed practical',1);p.write_text(s)
p=ROOT/'docs/graveyard-resources.md';s=p.read_text();s=s.replace('## Active enemy research','## Earlier enemy research (resolved in536)');p.write_text('''# Current status: preview536

The practical third-level milestone is COMPLETE.46 original vulture images and
independent colors, four bone-platform colors, shared HUD and hyena choices are
installed. Native timing/gameplay/effects and unsupported choices are explicit.
Full route516 reaches visible Stampede; current536 final fight544 is inspected.
See [delivery review](graveyard-delivery-review.md) for complete qualifications.
The public503 progress/fixture notes below are historical; their former active
enemy work is now resolved. Reuse current fixtures for future concrete defects.

'''+s)
p=ROOT/'docs/next-levels-status.md';p.write_text('''CURRENT546: Graveyard practical milestone COMPLETE. Public536 installs46
original vulture images/independent colors and four bone-platform colors,
retaining shared HUD/hyena/scenery/cub/music choices.531/540 focused checks,
532/539 live UI and538/541 native Setup/publication pass. Full route516 reaches
visible Stampede; current536 final fight544 is inspected. Native gameplay/effect
sounds and unsupported leaves remain explicit. Read root
docs/graveyard-delivery-review.md. Next The Stampede: inspect its special-scene
renderer; do not infer Graveyard layers or wider viewport support there.
Earlier active notes below retain their historical scopes.

'''+p.read_text())
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''

## Elephant Graveyard practical delivery525..546

Public536 installs46 original vulture phase images with independent MD bank3
colors; native bank5 comes from prepared original2F727. Original animation
streams/idle/takeoff records establish pairs; native timing/gameplay retained.
Five native descriptor owners, physical draw binding and native normal palette
guard preserve unknown owners/flashes. Existing art/gameplay and other prepared
banks retained. Shared native bone drawings remain; four actual bone owners get
independent prepared MD palette2 with normal bank7 fingerprint/identity indices.
No one/two-pixel bone edits, background/game/audio/state-schema changes.
531 PASS12 vulture controls/data,532 PASS5 actual live UI;534 bone proof,
540 PASS6 reuses537 captures after correcting inherited verifier schema,
539 PASS5 actual live UI;538 actual native Setup,541 installed publication.
Current536 late checkpoint544 confirms final hyena C58C74/normal6/mapped pose,
so no speculative ownership expansion is required. Full route516 through bonus
to visible Stampede is reused with unchanged game/frontend/audio/save objects;
local presentation changes receive scoped checks and current continuations.
Practical third-level goal complete; native behavior/unsupported MD limits are
in root docs/graveyard-delivery-review.md. Next The Stampede special scene.
''')
extra=('docs/HANDOFF.md','docs/graveyard-goal.md','docs/graveyard-resources.md','docs/graveyard-delivery-review.md','docs/next-levels-status.md','engine/docs/devlog.md','tools/pride_arena_history.py','scripts/RunInstalledPreview.ps1','game-data/install.json','dist/installed-preview536/package.json','engine/runner/tlk_resources.c','engine/runner/tlk_wide.c','engine/runner/tlk_md_sprites.c','engine/runner/tlk_md_sprites.h','engine/runner/tlk_graveyard_enemy_metadata.h','engine/runner/tlk_graveyard_bone_metadata.h','tools/graveyard_sprite_catalog.py','tools/graveyard_vulture_pairs.json','tools/pride_sprite_catalog.py','tools/build_graveyard493.py','tools/build_graveyard530.py','tools/build_graveyard536.py','tools/check_graveyard515_route.py','tools/check_graveyard516_route.py','tools/check_graveyard542_late.py','tools/check_graveyard544_fight.py')
paths=[Path(__file__),*reports,build,helper,late,*[ROOT/name for name in extra]]
checks=dict(full_level_and_stampede=True,current_final_fight=True,independent_supported_resources=True,installer_prepared_and_policy_checked=True,actual_windows_inspected=True,settings_and_prior_assets_preserved=True,focused_checkpoint_strategy=True,native_limits_documented=True)
out=ROOT/'build/graveyard546-delivery';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='PASS',practical_third_level_complete=True,universal_md_parity=False,checks=checks,binary_sha256=digest(exe),prepared_sprite_sha256=digest(packet),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('THIRD_LEVEL_PRACTICAL_MILESTONE_COMPLETE; public536; next Stampede',flush=True)
