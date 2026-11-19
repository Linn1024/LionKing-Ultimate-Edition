"""Record the public two-level delivery and preserve the remaining all-levels goal."""
from audit_scenes import ROOT
p=ROOT/'docs/HANDOFF.md';s=p.read_text();a=s.index('Active all-levels goal');b=s.index('\nPublic771,',a)
s=s[:a]+'''Active all-levels goal, explicitly requested2026-11-11. Public **849** now
delivers practical Hakuna Matata and Simba's Destiny resources. Read
[delivery/evidence/limits](hakuna-destiny-delivery.md), then
[all-levels progress](all-levels-progress.md). Launch `Play Hakuna Matata MD.cmd`
or `Play Simbas Destiny MD.cmd`; separate defaults preserve existing settings.
860 installs player849, ScenePreparer787/scene-v3 and SpritePreparer822/sprite-v2
policy5 (1153 images, TLKNXT02/1808 bytes) together. Existing HUD cache-v1 already
contains the adult portrait; no HUD re-extraction change.861 verifies both
actual CMDs,320-wide clients and selected new leaves. Binary SHA256:
79965061d4fe2910ccf4b7cc839cb83b8e7b7e66c749418b6b01768ca524b7d5.

Background rules and prepared samplers are proved per scene, not inferred from
decoded assets. Actors include55 gorilla and176 later-actor links, actual
ownership/normal palettes, frog bank5 alias and unknown/flash native fallback.
Adult MD HUD, independent5/6 level/death music, native-music isolation, Hakuna
shared cub cues/roar14, independent cub death movement and normal gorilla
recovery11 are delivered. Native other AI/timing, stage-owned enemy effects,
adult effects/death movement and fall/final-life presentation remain explicit.
Do not claim universal MD gameplay/audio or every-pose parity.

846 proves40/430/40 and281/430/281, independent native death cues, native output
preservation and no death-song overlap.850/853 prove death movement/current save/
retry and actual gorilla59->11 token; final landing stays59.854 actual cub/adult
death windows pass.856 final selected gorilla route reaches healthy Destiny;
it does not visit normal recovery, separately exercised850.818 traverses all
Destiny into Be Prepared7 after bonus13;44500.state is the next native checkpoint.
Original824 provides valid scene7 captures and43000.State, but its intended38000
start did not exist: it actually replayed the movie from startup. That script
now requires existing36000 and asserts its loaded field. Original834 uses actual
36000 plus research health1 and observes adult430/retry281; no shipped cheat.

Next: Be Prepared7, Simba's Return8, Pride Rock9/final fight, ending and bonus
resource review. Continue from saved checkpoints; no repeated earlier-level
matrix or old development-save migration. All-levels goal stays active.
''' +s[b:];p.write_text(s)
p=ROOT/'docs/all-levels-progress.md';s=p.read_text();s=s.replace('Public player remains771. This is progress, not a remaining-level delivery.','Public player849 now delivers practical Hakuna/Destiny resources; see\n[delivery and limits](hakuna-destiny-delivery.md). The all-levels goal remains active.')
s=s.replace('Original MD824 resumes38000, observes6/7 through49000 and saves41000/43000/46000.','Original MD824 observes6/7 through49000 and saves41000/43000/46000.\nIts intended38000 start did not exist; it actually ran from movie startup.\nThe corrected script requires existing36000 and asserts the loaded field.')
s=s.replace('hakuna826-windows/report.json','hakuna826-actors/report.json').replace('hakuna831-windows/report.json','hakuna831-hud/report.json')
a=s.index('Remaining Hakuna/Destiny work:');b=s.index('Reports: build/',a)
s=s[:a]+'''Public849/860 supersedes the private status above. Independent level/death
music for both levels now follows actual health-death/retry.846 observes
40/430/40 and281/430/281; selecting native death instead yields track/0/track.
Native PCM/picture/guest remain preserved, selected MD holds have native peak0.
Original834 actual36000 Destiny save plus research health1 produces original
430 at36157 and281 at36491. Native fatal-hit fixtures use research health1
only during fixture authoring; the published player has no health injection.
The common native C35A82 fatal controller is observed for both cub and adult.

849 also delivers Hakuna shared cub roar/hurt/roll/bounce cues, roar14, separate
cub death movement and selectable gorilla normal landing recovery11 rather
than59.847 observes the actual loaded native C27D43=59; original MD E94D4=11.
Alternate/final landing C27D9D remains59. This is a reviewed native adapter,
not a runtime cartridge-code reader or art-linked timing choice. Other AI
stays native.850 qualifies native picture/state, motion independence/current
save/retry and recovery selection.853 corrects the roar input fixture: press
after landing/recharging rather than hold during a saved jump. It proves14
and PCM10; no game fix was needed for the earlier no-edge fixture.854 actual
Windows cub/adult death clients show visible original pixel art; eight colors
are sufficient, and a >8-color validator was corrected rather than changing art.

858 actual isolated Setup imports coherent scene3/sprite2 policy5 and preserves
other payload hashes.859 qualification/860 publication update both native
preparers, player and installation.861 actual new CMDs use separate settings,
320 viewports and all new MD leaves; existing preferences remain untouched.
856 final selected gorilla route reaches healthy Destiny. That input route
does not visit normal recovery;850 separately exercises its real token seam.
Neither this route nor native-gameplay Destiny818 proves universal MD AI.

## Next steps

1. Continue Be Prepared7 using native44500 and original MD43000 checkpoints.
   Establish original initialization, layer/scroll, palette and animated-tile
   recipes before enabling readiness. ROM palette24EF66 is known, not a full
   renderer. Prepared actors require actual owner/bank review.
2. Continue Simba's Return8, Pride Rock9/final encounter and ending, then finish
   applicable bonus resource reviews. Preserve earlier independent choices.
3. Later enemy-specific effects and adult death movement remain native where
   no adapter is advertised. Address concrete noticeable gaps, using original
   call-site/controller evidence rather than audio logs' unreliable A5 value.

''' +s[b:]
s+='''\nDelivery reports: build/hakuna834-death/report.json, hakuna842/build-report.json,
hakuna846-music/report.json, hakuna847-tokens/report.json,
hakuna849/build-report.json, hakuna850-behavior/report.json (roar fixture
superseded by853), hakuna853-roar/report.json, hakuna854-death/report.json,
hakuna856-selected/report.json (normal-recovery visit unproved, healthy exit
proved), hakuna858-setup/report.json, hakuna859-qualified/report.json,
hakuna860-publication/report.json, hakuna861-installed/report.json.
Source baselines848/857 preserve pre-change audio/resources and Setup/launcher.
''';p.write_text(s)
p=ROOT/'docs/background-audit.md';s=p.read_text().replace('Public771/default Setup remain scene-v2 pending coherent actor/resource delivery.','Public849/860 and default Setup now publish scene-v3 with the actor/resource\ndelivery.861 verifies actual direct Hakuna/Destiny CMD clients. Readiness7\nremains false: the next scene still needs its own layer/initialization evidence.');p.write_text(s)
p=ROOT/'engine/docs/devlog.md';s=p.read_text()+'''
### Public849: Hakuna/Destiny music, death, meaningful timing and installation

Original834 resumes actual36000 MD save, research health1, and observes adult
health-death430/retry281. Native fixtures confirm shared fatal C35A82 for both
ages. Extend death state/music ownership to actual5/6 descriptors; independent
track/death children inherit existing music groups.846 proves40/430/40 and
281/430/281, native-death alternatives, unchanged native PCM/guest/window and
no selected death-song overlap. No runtime health injection was shipped.
847 observes gorilla native normal landing C27D43=59. Original MD E94D4=11;
849 independently adapts that loaded token, leaves alternate/final59 alone.
Extend reviewed shared cub roar14/effects and death movement to Hakuna, with
scene-normal palette guards.850 motion/current save/retry/native preservation
and actual boss token pass.853 delayed roar input fixes the harness's missing
edge, proves14/PCM10; no unnecessary game change.854 real Windows cub/adult
death captures pass; valid eight-color pixel art required a corrected validator.
858 actual Setup imports scene-v3/helper787 and1153-image sprite-v2/helper822
policy5, retaining HUD cache-v1 and other payloads.859 qualifies scoped evidence;
860 publishes849, updates both default preparers/data/launcher and preserves all
existing settings/assets.861 actual new Hakuna/Destiny CMD clients and MD leaf
choices pass.856 final selected boss route exits healthy; normal recovery was
not visited on that route and remains separately exercised850. Native other
AI/enemy effects/adult death movement remain explicit. All-levels goal active.
Original824's missing38000 save caused a movie-start replay; actual scene7 VDP
captures/saves remain valid. Script now asserts existing36000 load. Use saved
native44500 and original43000 for Be Prepared, not earlier-level replays.
Source baselines832/848/857 registered; neither framework submodule edited.
''';p.write_text(s)
p=ROOT/'README.md';s=p.read_text();s='''Current Windows preview849 adds Hakuna Matata and Simba's Destiny resources.
Launch `Play Hakuna Matata MD.cmd` or `Play Simbas Destiny MD.cmd`.
Each shortcut has separate defaults; existing settings are preserved.
See [current handoff](docs/HANDOFF.md), [delivery and limits](docs/hakuna-destiny-delivery.md)
and [active all-levels progress](docs/all-levels-progress.md). Remaining levels
through the ending are still being implemented. Entries below are historical.

''' +s;p.write_text(s)
