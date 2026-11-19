"""Record qualified Hakuna/Destiny actor, HUD and route progress."""
from audit_scenes import ROOT
p=ROOT/'docs/HANDOFF.md';s=p.read_text();a=s.index('Private802');b=s.index('\nPublic771,',a)
s=s[:a]+'''Private829 now includes the verified Hakuna/Destiny backgrounds, independently
selected cub/adult art,55 gorilla pose mappings and176 reviewed later-actor
links. Helper787 prepares scene-v3; helper822 prepares1153 sprite images,
policy5 (specific repertoire hash),1808-byte TLKNXT02. Use those private
packages together. Adult MD HUD portrait already exists in HUD cache-v1;
829 enables the actual adult upload, with no new HUD package. New world-object
frame/palette leaves and Destiny monkey frames are independent choices.
825 verifies231 original-art mappings and514522 sampler pixels, flash fallback,
frog bank5 alias, unrelated-image preservation and unchanged gameplay/palettes.
816/817 cover actual enemy/world/monkey owners;826 actual Windows frogs and
Destiny clients pass.830/831 verify native/guest preservation and actual adult HUD.
Full Destiny route818 reaches healthy Be Prepared7 after bonus13;44500.state
is the next native checkpoint. Original MD reference824 provides scene7 saves
and VDP captures, including43000.State; do not replay earlier levels to reach it.
Public Setup/helper/launcher remain771 with scene-v2/policy3. Publish all
dependencies together after noticeable sound/death and gameplay work. Native
gorilla AI/timing and most later effects remain; do not claim full MD parity.
See progress for precise ownership, current packages and remaining levels.
''' +s[b:];p.write_text(s)
p=ROOT/'docs/all-levels-progress.md';s=p.read_text();a=s.index('Remaining actor work is substantial:');b=s.index('## Next steps',a)
s=s[:a]+'''Private815/823 extend actual reviewed actor ownership: Hakuna hanging/jumping
spiders, frogs, logs, life icons/text and shared defeat puffs; Destiny jaguars,
monkeys, roots/trunks, boulders/fragments, pickups and effect owners. Ownership
requires exact scene descriptor, draw backlink, pose and normal palette.
Native flashes and unmapped art remain native. The frog shares native defeat
art in bank5 rather than its usual bank0; the new bank-aware sampler permits
only that scene/role/owner exception, preserving the original sampler API.
World objects frame/palette leaves and Destiny monkey frames are now independent.
Choices resolve per scanline, never by searching settings for every pixel.

810/813 expand the gorilla37 to55 pairs using valid original action operands,
including throwing/arm, turn/roar and landing-recovery art. Some original MD
phases reuse art where SNES changes it. AI/timing remains native. A possible
normal landing59 versus11 update pause needs actual VM-event confirmation
before any gameplay adapter; final landing has59 on both. Do not treat control
operands as timer bytes or construct complex phase variants for unseen frames.

Actor metadata now has176 exact/reviewed links (151 observed and25 bounded
repertoire matches). Native helper822 imports1153 images with sprite-v2 policy5
and its specific repertoire hash. It supersedes814's earlier policy hash even
though image count and generation match.825 imports prepared data through the
actual C sampler:231 mappings,514522 original MD RGB555/transparent pixels,
frog alias and flash guard pass. All aggregate gameplay, shared palettes and
death data remain unchanged. Unrelated prior artwork stays byte-identical;
newly reclassified actor keys intentionally use reviewed original MD images.

816 verifies native/guest preservation and independently selected actor frames
and colors.817 covers opening spiders/frogs, saving28200 for direct work.826
verifies real Windows clients with the final822 package: visible frog art and
Destiny world presentation, with jaguar/monkey sampling across the segment.
It is not a close-up screenshot of every jaguar pose.818 traverses all Destiny
from37000 to46000 with MD resources, reaching healthy Be Prepared7, health8,
lives6. Bonus13 is entered and returns; its resource audit is still pending.
Useful next-level native save: build/destiny818-route/later.state at44500.
Original MD824 resumes38000, observes6/7 through49000 and saves41000/43000/46000.
Be Prepared's palette source is ROM24EF66. Background readiness7 is still false;
generic decoding does not prove initialization, layer or scroll coverage.

Private829 enables common HUD through Destiny and the adult portrait. The
existing HUD cache-v1 range8EC14..8FDC6 already contains cub8F1F8 and adult8F318
portraits, each288 bytes; original VRAM D440 proves actual stage5/6 uploads.
No new HUD helper/data is needed. Adult render choice follows saved native age.
830 verifies native picture/guest preservation and independent life-only choice;
831 actual Windows capture shows the adult MD portrait and meters.

Remaining Hakuna/Destiny work: original-sourced effects/death music and meaningful
boss gameplay review, then coherent installation and separate direct launchers.
Original780 health-death command430 is observed at29453; current audio death
scope excludes5/6 and must be reviewed. A5 in original audio logs is not reliable
owner proof; bind actual call sites/controllers. No new audio/gameplay parity
claim accompanies these actor/HUD changes. Public771 remains unchanged.

''' +s[b:];s=s.replace('1. Finish remaining Hakuna/Destiny actors and unobserved gorilla action drawings;\n   reuse existing prepared images after ownership review. Keep unknown art native.\n2. Review meaningful effects, roar/death and boss gameplay differences. Do not blindly extend','1. Review meaningful effects, roar/death and boss gameplay differences. Do not blindly extend').replace('3. Prepare/install resources','2. Prepare/install resources').replace('4. Continue Be Prepared','3. Continue Be Prepared')
s+='''\nCurrent reports: build/hakuna815/build-report.json, hakuna816-actors/report.json,
hakuna817-opening/report.json, destiny818-route/report.json,
hakuna822-helper/build-report.json, hakuna823/build-report.json,
next824-reference/report.json, hakuna825-prepared/report.json,
hakuna826-windows/report.json, hakuna829/build-report.json,
hakuna830-hud/report.json, hakuna831-windows/report.json.
Additional source baselines811/820/828/832 are registered before changes.
''';p.write_text(s)
p=ROOT/'engine/docs/devlog.md';s=p.read_text();s+='''
### Private829: Hakuna/Destiny actors, adult HUD and next-level handoff

Gorilla art expands37 to55 valid original animation-pose mappings. Reviewed
actor metadata adds176 links for spiders/frogs/logs, jaguars/monkeys/roots,
boulders/fragments and pickups/effects. Actual owner/scene/backlink/palette
guards preserve native flashes and unknown art. New independent world-object
frames/colors and Destiny monkey frames; frog puff has a narrowly scoped bank5
alias through a new API, leaving legacy sample paths unchanged. Helper822
prepares1153 images with the final policy5 repertoire hash and TLKNXT02.
825 verifies231 mappings/514522 original MD pixels, native fallbacks and
unchanged gameplay/palettes.816/817 focused ownership/independence/native-state
checks and826 actual Windows clients pass.818 completes Destiny into healthy
Be Prepared, including an observed bonus13 entry/return;44500 save is ready.
824 original MD reference provides subsequent VDP captures and43000 save.
829 enables prepared HUD artwork through6, choosing adult8F318 instead of
cub8F1F8 from the existing cache-v1 range. Original VRAM D440 proves both
uploads.830 native/guest/life-only checks and831 actual adult HUD pass.
Public771 remains unchanged pending sound/death/gameplay and coherent installer
delivery. No universal MD AI/effects claim, old-save migration, full-engine
matrix or framework-submodule edits. Baselines811/820/828/832 registered.
''';p.write_text(s)
