"""Record the final Destiny boundary and private Be Prepared background milestone."""
from audit_scenes import ROOT
p=ROOT/'docs/HANDOFF.md';s=p.read_text();needle='Next: Be Prepared7, Simba\'s Return8, Pride Rock9/final fight, ending and bonus\nresource review.';assert needle in s
s=s.replace(needle,'''Private866 now adds Be Prepared's verified uniform-half-X/fixed-Y background
with actual descriptor04E5 and saved raster camera history. Existing scene-v3
already contains its complete static data; no package/schema expansion needed.
864 proves initialization08E7A4 disables the previous scene's line table; stale
C610 words must not be treated as active scroll. Names, used tiles and64 colors
match seven actual original VDP captures.867 matches501760 tokens through the
prepared-cache C sampler.868 source independence/native guest/picture/current
save pass;869 actual320-wide Windows view passes. Public remains849 pending
Be Prepared actors/audio/gameplay and following-level delivery. Native actor/HUD
art is deliberate fallback here, not a claim of MD sprite coverage7.

Preferred next native fixture: `build/destiny863-handoff/be-prepared.native.state`
at44500; paired input `after44500.polled.tape` in the same folder.863 completes
Destiny with final installed849 MD resources, reaches healthy7 (health8,lives5),
and establishes the exact7091 consumed-poll boundary. Do not restart its input
at poll0 of the older37000 tape. Original MD `build/next824-reference/43000.State`
is the nearby7 reference; verify loaded frame/level before observing it.

Next: Be Prepared7 actors, sound and meaningful gameplay, then Simba's Return8,
Pride Rock9/final fight, ending and bonus resource review.''');p.write_text(s)
p=ROOT/'docs/all-levels-progress.md';s=p.read_text();s+='''
## Be Prepared background and direct handoff863-869

863 runs the final installed849 Destiny stack once, authoring the exact next
input boundary instead of replaying Destiny for each later check. It ends44500
in healthy Be Prepared (health8,lives5), after7091 input polls. Use
build/destiny863-handoff/be-prepared.native.state and its
after44500.polled.tape (15625 words). Current frontend save is current.state.
This supersedes818's older native44500 fixture as the preferred starting point.

Original7 background owner08BA60 uses update08E77C and init08E7A4. Init clears
C60C and sets VDP register11 to full-plane scroll; C610 row words are stale
Destiny data. Actual uniform completed offsets are at VRAM FC00/FC02. Background
X is half the displayed camera, Y=0. Source map24A15C is3584 bytes; tiles24A720
are31008 bytes; palette24EF66 is ordinary ROM. Seven original VDP samples have
identical complete names, every used background tile and all64 palette colors.
No extra tile/palette animation is established or needed for these samples.

Private866 implements only this reviewed background and its exact native04E5
eligibility using existing saved raster history. Existing scene-v3 already
contains the full data.867 loads that prepared cache and matches501760 original
pixel tokens.868 independently selects background/colors, preserves native
picture/guest state and verifies current save/restore.869 actual320-wide Windows
client shows lava columns and foreground/actors clearly. Public849 remains
unchanged. Next inventory actual7 actor owners/poses/banks, then original sound
call sites and noticeable gameplay before claiming a complete level resource set.
Native8/9, final fight/ending and bonus resources remain in the goal.

Reports: build/destiny863-handoff/report.json,
be-prepared864-background/report.json, be-prepared866/build-report.json,
be-prepared867-sampler/report.json, be-prepared868-choices/report.json,
be-prepared869-windows/report.json. Baseline865 registered before engine changes.
''';p.write_text(s)
p=ROOT/'docs/background-audit.md';s=p.read_text().replace('Readiness7\nremains false: the next scene still needs its own layer/initialization evidence.','Public849 readiness7\nremains false; private866 follows the independently verified recipe below.')
s+='''
## Be Prepared864-869 (private866)

Native863 at44500 has two enabled/decoded224-line Mode1 BG layers and no BG3;
do not infer that identity from original MD plane numbering. MD08E7A4 creates
background08BA60, clears line-table pointerC60C and selects uniform full-plane
scroll with VDP register11=0.08E77C sets half camera X and Y=0. The old C610
line words belong to the preceding Destiny scene and are unused here. Completed
VDP plane offsets atFC00/FC02 establish the displayed camera, avoiding next-field
RAM ambiguity. Actual map/used tiles/all64 palette colors match all seven
original824 captures42000..48000. Map24A15C/3584 bytes, tiles24A720/31008,
palette24EF66. Uniform horizontal hardware repeat is observed; vertical scroll
stays0. No extra background upload/color recipe is inferred.

Private866 enables readiness7 and native descriptor04E5 background history;
public849 remains unchanged.867 imports existing scene-v3 and matches501760
original C-sampler tokens.868 native picture/guest/source/save controls pass;
869 actual320-wide Windows client passes. This does not certify stage7 actors,
foreground art, effects, HUD or gameplay as full MD equivalents.
''';p.write_text(s)
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''
### Private866: Be Prepared background after the public two-level delivery

863 finishes Destiny with final installed849 MD resources and authors a precise
44500 checkpoint/input tail:7091 consumed polls, healthy Be Prepared7. Original
864 shows08E7A4 clears C60C and selects full-plane scroll; old C610 line words
are stale Destiny data.08E77C uses half displayed camera X, Y=0. Complete names,
used background tiles and64 colors match seven original VDP captures.866 adapts
only this background, exact04E5 native scene and existing saved raster history.
Scene-v3 already contains all required static data; public849/data unchanged.
867 prepared-loader sampler matches501760 original tokens;868 independent
sources/native picture+guest/current save pass.869 actual320-wide client passes.
Next actual actor ownership/pose/bank inventory, sound call sites and meaningful
gameplay, then8/9/final ending and bonuses. Baseline865 preserves source evidence;
no framework edits, old-save migration or unrelated earlier-level tests.
''')
