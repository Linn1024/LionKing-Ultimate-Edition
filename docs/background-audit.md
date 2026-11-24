## Delivery7175: SNES artwork boundaries and positive Pride wrap

Supersedes7116's use of MD row numbers on SNES artwork. Sources/planes are
still independent. No asset completeness, new background plane or save-format
claim; capability strings and existing per-scene expanded-view recipes remain.

All five scenes retain their own native Mode1 BG2, 8px tiles, BGSC49 hex
(512x256 VRAM name-table ring), captured tile base/CGRAM/priority/math and
vertical scroll. BG1 remains the independently selected terrain; BG3 is HUD/text.
Normal SNES BG2 sampling addresses source y = (raster y + 1 + captured VOFS)&255.
The tall King panorama already supplies its decoded authored source row directly;
it must not receive that extra +1/VOFS or the old223-row truncation.

| Scene / initialization owner | Native artwork evidence and corrected optional motion |
| --- | --- |
| Pride Lands C00387 / C0080D | Original descriptor+1A supplies the45-row panorama, streamed into native VRAM. The initialized BGSC49 has a512-column horizontal period. Retain the existing negative added-margin extension before source zero. Positive columns past511 must use the original name-table wrap, not repeat column511. Current normal320x224 SNES-scenery/MD-gameplay fixture at2617 has camera1114/276, BG2 scroll208/33;45 physical right-edge columns expose the old smear (1260 changed pixels). Original256 picture and entire WRAM/native frame remain exact. Width800/height224 also exposes the defect; the already fitted tall panorama does not use this clamp and stays exact. |
| King C003B9 | Original descriptor+1A native map is64x31 cells (248 rows). Probe7170 shows row151 still plain sky and hill detail beginning at source152; hills include bottom shading through199, with a plain water join at200. Use quarter-rate before152, half-rate152..199, then the existing progressive water coefficient from200 through247. Normal raster row151 therefore belongs to the hills, while a tall source row151 still belongs to sky. Preserve the original MD camera/wrap accumulator and native sun/palette clocks. MD artwork retains its own152/192 displayed-row schedule. |
| Hakuna C00481 | Captured native VOFS is4 at entry and73 at the moving normal fixture; the MD Y5/16 estimate is not the same source coordinate. Native source bands8/144/240 lie in flat rows: the full probe has uniform source131..153 and223..255. Apply eighth/quarter/half horizontal rates to the actual selected native source row, not MD-camera Y plus raster y. Native waterfall tile uploads, vertical scroll, initialization and terrain remain unchanged. |
| Return C00517 | Native raster records change horizontal bands at displayed96 and152, corresponding to source97 and153 with VOFS0. Preserve these existing SNES joins while optionally using MD eighth/quarter/half depth rates. Do not impose MD displayed112/151 boundaries. Native color math remains captured (including the sub-screen phase). |
| Pride Rock C00549 / summit C007DB | Source96 crosses detailed clouds; source111..113 is horizontally uniform. Keep the whole upper cloud detail at half-rate until source112; use quarter-rate until the existing plain dark source184 join, then half-rate. The open summit fixture makes the corrected clouds visible (26118 normal-window pixels differ); the entry fixture's foreground hides this band and is not counted as positive visual proof. Retain the original native vertical origin, live color phases, firelight choice and later rain ownership. |

Evidence: build/fidelity7170-background-repro contains a research-only renderer
probe decoding native source rows/name tables from captured state, not synthetic
art or a guest-state patch.7172 contains matched normal/tall effects-on/off,
normal256/320 Pride and width-only controls, an original-clock AOT/LLE pair,
unchanged ending rain and original/pending pixel-difference bounds.7173 checks
all other main/bonus worlds and the four MD-background controls in normal/tall
views; native frame, full WRAM and displayed PNGs match before/after. Stampede
uses its special scene path (stage_detected=false is expected there); the
selected ordinary and bonus controls are initialized and nonblank.7174 actual
Windows captures reviewed for King, clouds and normal Pride; preliminary black
Pride captures were taken before its first render and superseded after waiting
for a nonblank game frame. Original source/depth clocks, actors, audio, prepared
assets and both frameworks remain unchanged. No full new TAS/walkthrough claim.

## Current delivery7147: independent sprite colours

Delivery7147 adds independent custom colours to the existing semantic sprite palette fields, HUD and caption palette fields. Each resource keeps separate SNES/Genesis shade edits across all levels. The old per-level foreground/background/objects shade maps remain readable and usable; an explicit sprite edit takes precedence for its original selected-source shade. No new source-choice nodes or gameplay/save binding changes. The editor is F12 > Artwork > selected sprite > Palette > Custom colours for this sprite, with subject drawings, original/pending previews, reset shade/current-source edits, live Apply, Undo and named preset import/export. Where a gallery is unavailable it can use the current scene subject shades and a before/after scene preview; a currently absent subject asks the player to visit its scene. This follows existing resource categories; it is not separate editing of each individual enemy instance or arbitrary separate animation frame. Whole-layer colours remain separate.

Sparse entries use sprite_colour.<stable palette resource ID>.<snes|md>.<RGB555> = <RGB555>. Active/draft transactions share a validated4096-entry limit with legacy colour entries. An independent hash lookup avoids a per-pixel scan. Semantic ownership is carried through native sprites, complete MD replacements, margin pieces, cub/adult death bodies, source-only shared drawings, HUD, captions, opening Timon and ride preview obstacles. Shared jaws/falling bones retain bone ownership with SNES colours; Mufasa farewell uses exact pose identity; animal heads/tails and adult/scripted hyenas retain their resource across poses. Original bank indices, transparency, brightness, colour math, guest state and frame timing are preserved.

Evidence:7132 C storage isolation/source/black/reset/malformed/capacity/encode-decode tests;7133 all14 source-off original/current displayed/native/full WRAM controls;7136 normal-view22 visible sprite-category recolour cases across ten main/four bonus scenes with unchanged native/full WRAM;7139 both palette-source hyena/gorilla/vulture tests;7140 native and moving death, Timon, and wrong-source no-leak controls;7141 existing wrapped checkpoint and original-clock compiled/interpreter exact, original/expanded default windows exact, expanded recolour and600-field throughput124.4 versus125.1 updates/sec locally; actual Windows picker/Undo/named-save/reload/live Apply under7138.7145 final candidate controls match relevant reviewed endpoints and the actual named preset loads. Some fixtures did not show the intended subject (Scar and a normal-view bone sample) and are not counted as positive sprite coverage. Not a new walkthrough/TAS certification or universal no-bug guarantee. New optional The Best scenery selections from7129 remain in place. Frameworks, audio/game objects, installed prepared data and asset formats unchanged. Frozen resource node source remains build/fidelity7110-scenery-colour-player/resources_public.c; it includes the maintained palette storage helper. Four presentation/storage/browser/data-reader objects replace7126.

## Current delivery7126: visual-effects audit

Delivery7126: visual-effects audit across all ten levels and four bonus areas, both artwork sources, normal and expanded views; representative mixed-palette checks. Invalid loading/death samples in the first72-case matrix are superseded by healthy fresh Graveyard, Stampede and Bug Toss checks in7124. Fixed custom object colours being omitted by the separately rendered shared death body and native adult death overlay. Fixed optional native-art depth motion and foreground firelight eligibility at the Pride Rock summit C007DB, using the existing scene9 band recipe and colour clock; rain continues to own its later palette phases. These are live presentation fixes. No guest code, audio, gameplay, asset formats or frameworks changed. Source-off death and summit windows/native/full WRAM remain exact against7116; effect-on tests retain native/full WRAM and show the intended visible differences. Both ostrich-ride fixtures, post-Stampede story and real ending rain checked old/new with matching displayed images and state hashes. Actual desktop-window captures under7125. Audit evidence7118/7124/7125; not a full new walkthrough or TAS certification, and not proof of every possible scene/camera position. The first-level story checkpoint needs its original640-pixel viewport and was not qualified by the new800-wide probe; existing7072 source-bound story evidence remains applicable.

## Delivery7116: source-independent native-art effects

Current delivery7116 /installed-preview7110 implements the YouTube granvillimus request with optional Genesis-style motion on SNES King, Hakuna, Return and Pride Rock backgrounds, and optional Pride Rock fire reflections while retaining SNES colours. F12 > Artwork > Scenery > Motion on SNES backgrounds offers each level independently; Pride Rock flickering firelight is separate. All are live presentation choices. Current presets and existing profiles keep their original default selections. Genesis artwork retains its established original motion/palette animation.

Native BG2 keeps its own raster/name table, tiles, vertical origin, priorities and existing finite/mirrored presentation extension. Only its horizontal row offset changes: King08BB28 uses152 rows at quarter camera,40 at half, then progressive water; Hakuna08DB82 uses its reviewed camera-selected8/136/96/272 table rates; Return08E7E8/08EA00 uses112/39/73 at eighth/quarter/half; Pride Rock08E2B0/08E532 uses96/88/40 at half/quarter/half. Tall views select the same authored native background rows before applying the adapted depth offset. This is a cross-artwork adaptation, not a new assertion that SNES/MD planes or authored boundaries are identical. Firelight applies the original08E502 three-phase colour delta to nearest phase2 shades of red-dominant native foreground colours. The existing saved200-initial/11-update clock, pause/reload and rain ownership remain; no invented timer or CGRAM edit.

Palette leaves now include Edit this level colours: per-level foreground/background/sprites-and-HUD shade edits, scrollable swatches, colour picker, source/current and pending paused previews, reset shade/layer. Custom maps affect source-selected colours before existing brightness/colour math; original artwork and guest palettes stay intact. Actual visible MD object shades are collected for editing. Up to1024 sparse edits persist as validated colour.level.layer.RGB555 entries in the existing profile and named preset import/export. Pure SNES normal-width custom edits explicitly enable presentation. Undo invalidates the preview; textures are cleared before renderer teardown. Live Apply does not restart a level. Palette edits and newly appended optional presentation IDs do not bind the gameplay save identity; an existing wrapped source-matched save stays loadable without rewriting it.

Focused7111/7114/7115 tests: four source-off wide previous/current full WRAM/native/window exact; moving King normal/wide and all other named levels normal show changed background pixels with exact guest endpoints. Isolated firelight visible at its original phase. Full SNES256-wide custom colours and Full MD objects work; Full MD source-off exact. C storage tests cover draft/live, isolation, reset, black, malformed input and actual file roundtrip. Actual Windows editor pick/Undo/named-save/load/live Apply, responsive settings, Hakuna/Pride effects reviewed. Original-clock AOT/LLE palette control exact; observed140.9 updates/sec at800x450 over600 fields, no universal FPS claim. No full walkthrough or TAS rerun. Only host/resources/UI/wide objects replace7104; game/audio/assets/frameworks and saved envelope formats unchanged. Broader all28/source/TAS goal remains open. Evidence build/fidelity7115-source-controls/final-report.json. Frozen resource source: build/fidelity7110-scenery-colour-player/resources_public.c.

## Delivery7085: original Hunt panoramas in tall views

Current delivery7085 /installed-preview7083 enables adaptive width and height for all three scrolling Timon Bug Hunt worlds11-13, with exact original descriptor ownership. Their native foreground uses one complete original world-map sampler throughout the tall picture, including the old224-row band, rather than stitching that band to separately admitted extra rows. Native BG2 uses its own original descriptor+1A3584-byte64-column28-row panorama; fit all224 authored rows to the tall view and retain the existing mirrored512-column presentation extension. Genesis foreground retains its verified complete map and16px normalized origin; Genesis background retains its independently verified fixed-scene recipe. No new layer correspondence or original MD renderer-completeness claim. Source artwork/palettes remain independently selectable; original SNES art is not redrawn. This expanded-view work does not overturn7081's sampled original-art evidence.

Extend existing vertical sprite/queue admission only for the three owned Hunt scenes, so bugs in added rows are submitted. Source catch rules, movement, timers and rewards are unchanged. Existing free-view camera/finite-world limits are reused. Fixed Pumbaa arena, Stampede, cinematic and main-world source recipes stay. Tall Hunt camera keys11-13 and their exact descriptor are now validated in existing view-history13; no state-envelope version change or user-save rewrite. All three tall save/load roundtrips match uninterrupted full WRAM/native and displayed picture.

Focused7084 covers all three worlds with SNES and Genesis art at1024x768 logical view, original-sized old/new full WRAM/native/window equality in all six cases, final normal controls after the validator change, real moving Windows Hunt13 and the fresh source-matched King human route through Hunt into Graveyard. Original-clock compiled/interpreter whole WRAM/native match. Smooth-mode compiled/interpreter equality is not claimed. Large852x504 observed76.3 processed fields/sec; maximum1024x76851.9, so no universal60fps guarantee. Real Windows640x360 run59.7/sec. No full-game/TAS rerun.

Only pride_final_wide.obj replaces7075; current audio7075, resources/frontend7066, gameplay and all other linked objects retained. Installer reuses existing prepared data; ordinary settings/profiles/recordings/saves unchanged. Guided showcase Timon chapter is re-rendered from current genuine human input at640x360 and kept15s; previous full video retained. Broad all28/source/TAS goal remains open.

Follow-up steady-state check:1024x768 logical view, same genuine Hunt13 human-input suffix, fields11700..12100 after150-field warm-up and without final capture/save overhead, observed63.11 rendered updates/sec. Earlier51.9 processed-fields/sec was a short cold120-field capture/save run. This is local throughput headroom, not a universal no-drops guarantee. Evidence:build/fidelity7084-timon-area-check/max-steady/report.json.

## Delivery6985: expanded weather, background layers unchanged

Current6985 /installed-preview6983 fixes ending rain covering only the old small weather canvas after the expanded-ending camera fix6981. Use the preserved6977 slot2 and natural720-field continuation to114585, then120 live rain fields to114705. Current852x503 presentation, SNES art with MD weather, reaches six native submitted rain pieces. These remain the actual C585D0/C2F33E screen-fixed rain particles; the scene is C007DB.

Repeat the current source particle field into added presentation space: MD motion uses320x224, native motion256x224. Keep the current source positions, pose, flips, OAM ordering, source artwork and independent palette. The added copies are presentation only, not extra guest actors or new RNG/motion/emitter clocks. Rain uses a single screen anchor rather than generic HUD top/middle/bottom bands, preventing a falling drop changing vertical anchors as it crosses a HUD band. Wrap each row over224 and each source drawing across its weather width; both native tile and complete MD-art passes cover the added view. Normal selected console-sized224-height rendering is unchanged. Cache selected viewport once per compositor draw, retaining the earlier5840 resource-lookup optimization.

Focused6984 mixed120 fields: exact whole WRAM/native frame and gameplay old/new. Native-art/MD-weather, MD-art/MD-weather and native-weather combinations checked; both artwork console controls are pixel-exact old/new. A pre-rain large-view control is completely unchanged. Exact current wrapped seed is used for default style; alternative-source controls use its bounded intact TLKSTAT1 payload, no wrapper identity rewrite or guest patch. Real Windows old/new captures reviewed; rain changes appear in all nine thirds of the physical window, including top/bottom and both sides. Local120-field dummy-video throughput102.8old/101.5new, including startup, not a full-game performance guarantee. No unrelated full walkthrough.

Only pride_final_wide.obj changes on6981. Existing scene layer/scroll/initialization recipes, background renderer, finite ending camera, ending clock, audio, gameplay, source choices, formats, user saves/settings/presets and installed assets retained. No new background layer or renderer-completeness claim. Previous zoom fix, Scar retreat, hit-band/fountain/vulture/preset fixes retained. Hakuna material/ledge limitations and broad all28/source-coverage goal remain OPEN.

## Delivery6981: established ending layers in expanded view

Current6981 /installed-preview6979 fixes the sudden zoom when entering the summit/post-Scar ending in a tall adaptive window. User slot2 preserved6977 at113865, C007DB phase3, Simba676/134, camera484/15, SNES artwork/Genesis gameplay,2560x1511 window. User confirmed the report means Simba/scenery suddenly enlarge, not wrong world-camera movement.

C007DB had an existing wide renderer but was excluded from the free-height area compositor. WideWidth consequently selected380x224 instead of852x503, enlarging the entire image to fit the same physical window. Permit this established summit/postfight scene in TlkWideAreaSupported. Retain the finite scripted console camera in tlk_camera.c: no free-width feedback into cinematic tracking, original script progression or game updates. Only while drawing a taller area with the active MD camera, centre its selected console canvas inside the expanded presentation; the original native-camera branch keeps its map-range logic. Simba/artwork retain gameplay pixel scale. No new source choice or setting.

Background evidence: actual C007DB native Mode1 schedule (captured early rows labelled9), TM19/TS0, BGSC65/73/72, scroll484/15 and BG2 30/0, math48/0. This scene already retains the verified native foreground map and established postfight BG2 renderer/palette schedule. Use those same layer/scroll/initialization records in the existing area compositor; no invented layer, source-plane correspondence, edge-repeat recipe, new decoded asset, camera transform or broader MD-renderer completeness claim. The current SNES-art foreground remains native_layout. Expanded picture reviewed with the cliff and scenery visible at the original pixel scale.

Focused6980: same saved initial two fields and720-field natural ending continuation preserve entire WRAM/native frame and Simba state old/new. Actual Windows initial captures reviewed: prior380x224 presentation versus new852x503, centred Simba with no close-up. Original320x224 old/new whole WRAM/native frame/window exact. New720-field dummy-video continuation measured61.1 processed fields/sec; this is not a full-game performance gate. Scope is the summit/postfight world, not a redesign of the subsequent full-screen sunrise illustration or credits. No unrelated full walkthrough.

Only pride_final_wide.obj changes on6976; Scar retirement, earlier hit-band/fountain/vulture/preset fixes retained. Source camera, audio, gameplay, user settings/current saves, named presets and installed assets preserved. Hakuna material/ledge limitations and broad all28/source-coverage goal remain OPEN.

## Delivery6976: Scar escape bounds, background unchanged

Current6976 /installed-preview6974 fixes Scar disappearing during his first Pride Rock retreat in the user slot1. Preserved6972 field103626, SNES visuals/Genesis gameplay,852x503 world view: first Scar C585E8 at1462/1536, camera748/1375, injured below zero health, actionC65F4B. By old field103716 he is removed from the active list at his unchanged position; his retained pose is not a live sprite and must not be revived by the renderer.

Original C672A8 compares Scar against cameraX-40 and cameraX+296, then cameraY+224. At103662 the live horizontal separation714 exceeds296 despite being inside the expanded picture. C67368 retires the defeated encounter before its actual escape movement. Enlarge only those three camera-bound operands by the existing live expanded viewport margins (right bound892 in this save). Keep ordinary query comparisons, source animation/movement and final caller-owned deletion. No actor/HP/position/velocity/result forcing or synthetic replacement sprite. Apply to all three owned Scar encounter descriptors, independently of artwork and AI source; original-size queries remain exact. Width/height come from the same active spawn camera as existing widened actor lifetime support. This is a viewport correction, not a new SNES/Genesis gameplay option.

Maintained wide margins API and Scar module register both compiled after-instruction and interpreter pre-instruction seams. Recompile only the existing nativeC6 part1e object for the added aot_pace hook sites; no generated game source or framework changes. Preserve all prior frozen audio/cinematic objects. Scene C00549 planes/scroll/initialization/background remain unchanged.

Focused6975: pre-query field103656 guest/native/window exact. At103746 old Scar is absent, new Scar is active at1229/1518 in the actual escape; Simba position/health/spares agree. Real Windows old/new captures reviewed, visible new leap instead of empty platform. By103986 both pictures agree after departure; caller retires Scar normally. Original-size old/new whole WRAM/native frame/window exact. Expanded original-timing compiled/interpreter whole WRAM/native frame/window exact through103746. Gameplay hashes intentionally differ in the widened retreat after old premature retirement; no false rendering-only equality claim. No unrelated full walkthrough/TAS rerun.

Only pride_final_wide.obj, tlk_scar_activation.obj and native_c6_part1e.obj change on6970. User settings/current saves/presets and installed asset data retained. Prior Hakuna/Destiny hit bands and fountain/vulture fixes retained. Hakuna ledge material limitations and broad all28/source-coverage goal remain OPEN.

## Delivery6970: isolated hit blanks, no new background layers

Current6970 /installed-preview6966 fixes two reproduced hit-related black bands in the large SNES-art/Genesis-gameplay window. Slot4 Hakuna C00481: hold RIGHT continuously from preserved field48884. At48921 Simba still has3HP, but two isolated native forced-blank scanlines were enlarged into269 physical black rows. Slot1 Destiny C004B3: stay still from59396; at59658 Simba has5HP and15 isolated blank rows become242 physical black rows. These are hurt/streaming presentation flashes, not death-centering evidence.

Extend the existing initialized-world isolated-blank-line presentation policy to these two world descriptors. An isolated forced blank borrows the nearest completed nonblank world row; ordinary dark rows and fully blank fades retain captured state. The policy is restricted to the expanded area compositor. No guest instruction, actor, damage, health, camera, collision, sprite upload or original-height rendering changes. Existing scene planes/scroll/initialization remain unchanged. No new background recipe or asset coverage claim.

Focused6967 replays preserve whole WRAM, native frame and gameplay at both exact hit endpoints. Real Windows before/after captures show269/242 full black rows becoming0/0; private capture-only wrapper pumps window events before UI shutdown, never shipped. Original-size control windows are exact old/new. Healthy initial Hakuna presentation is also exact. No unrelated full walkthrough. Only pride_final_wide.obj changes from6960; fountain/vulture/browser/preset fixes retained. Original saves and settings preserved.

Hakuna mixed-terrain black ledge rectangles and the left platform remain OPEN: current SNES material-to-Genesis layout matching is visibly imperfect. Candidate material-variety and silhouette changes were rejected after image review (no improvement or wrong repeated textures). md_assets.c/.h restored to their prior sources, original linked object retained. This delivery does not claim those geometry/art issues fixed. Broad all28/source-coverage goal remains OPEN.

CURRENT6960: The current slot2 bottom-right hole is the32px below the two original fountain bases, exposed by the tall view. Continue existing live fountain body to the finite map edge; this is sprite presentation, not a new background layer or proof of original water below its source base.

CURRENT6778: Waterfall log cycling restored to original300px. Extra turns
are sprite presentation; scenery recipes unchanged. See Delivery6778 below.

CURRENT6765: Missing secondary Graveyard fountain reconstructed only from its
current factory-owned primary drawing; existing scenery recipes unchanged.
See Delivery6765 below.

CURRENT6755: Native tile decoding and per-draw correspondence reuse reduce
large-view rendering work. Scene addressing, layer/scroll/initialization,
edge recipes and capability reports unchanged. See Delivery6755 below.

CURRENT6724: First/second wide ostrich entries absorb the full measured camera
rebase and ease the presentation pan over512 actual ridden pixels. Separate
foreground/BG2 source phases preserved; normal viewport pictures unchanged.
See Delivery6724 below.

CURRENT6716: Solid-color free-view extensions removed. Native full panoramas or
selected captured-picture fitting cover supported tall main worlds. Native/MD
recipes remain independent; MD Exile fixed upper320 canvas reflected separately.
Source-authored flat skies, darkness/fades and fixed scene framing stay original.
See Delivery6716 below and current HANDOFF for source limits and evidence.

CURRENT6216: Pride and normal King native BG2 share the finite bottom-band policy while retaining their own scroll/colors. Ostrich free-size presentation uses an explicitly512-pixel authored running ring, independent of the console gameplay camera. Other layer/capability limits remain. See6216 evidence below.

CURRENT6199: Tall native Pride BG2 now uses a scene-specific bottom-anchored band and sky fill; other background extensions retain their existing capability limits. See Tall user-window evidence6199 below.

CURRENT6191: Ostrich strips retain selected console framing in wide/free view;
no new background layers, repeats or outside-strip rendering claimed. See
Console-framed ostrich rides6191 below. New1024-column normal-world walkthroughs
reach credits in both presets; Original camera/enemies.

CURRENT6175: Taller free view extends normal-world foreground/submitted actors.
Extra background bands use selected dominant boundary color; original224-row
plane schedules are retained, not claimed reconstructed beyond the viewport.
See Vertical free-view evidence6175 below and current HANDOFF.

CURRENT5787 DELIVERY: installed-preview5774 /494 choices393 MD leaves1703+44 images/policy140/helper5754/history10. Complete original MD main foreground maps enabled for Be Prepared/Pride Rock ONLY when both their terrain and foreground are MD; normal summit recipe unchanged. Compositor only, all helpers/assets/settings/choices/audio/gameplay preserved. Public audio5606 and bounded resources5702 stay frozen.
5779 nearby original Prepared47180->47240 and independent Pride practice1960->2000: whole guest/nativePPU/same-mode shortPCM preserved, MD AOT/LLE exact, nativeforeground and nativeterrain old/new pairs exact. Actual old/new5780 windows all VIEWED:4924/532 changed pixels, HUD component regions and actual-window/dump pixels exact.689/120 foreground fallback records become0 by real MD sampling. No whole-scene/final-TAS/zero-sprite-fallback claim.
Original5771 names/used tiles exact but its uniform-scroll check FAILED because it scanned unused fullscreen-mode0 words; summary assumption corrected5790 from unique actual original GPGX register arrays:Prepared43000/46000 mode0, mainPride54000 mode3. Correctly selected displayed entries uniform in four map samples. Live native visual maps5772 unchanged. No assumption about dedicated summit or arbitrary unsampled map mutations.
Initial apparent missingHUD was a preview-reading mistake: captured RGB pixels prove unchanged HUD. Source-priority experiment5782 had no observed picture difference and was DISCARDED; current maintainedwide restored exact5774 source with two added layout conditions only. Private5784 probe NEVER shipped. Failed5783 graphics.hud.meters test-profile typo corrected to graphics.hud.frames; remaining checks completed without rerunning valid cases.5786 qualification records all evidence and failures.
NEXT concrete remaining sprite gaps: two Pride lightning drawingsC68920/C68983 ->MD179BD4/179C9C source5763, fixture5766at2440 +5767ordinary.tape ->2740. Adult checkpoint blinkC2FD87/C2FDB4 plus dedicated checkpoint source routing (baseC01998 identicalMD79000), source5762/5765 fixture5768at47480. Return/Pride hyenaC1ABF6 and C58648 effects remain exact original attribution leads. King caption order/two-stage lifetime remains native. Broad28 reports and final unchanged original Genesis FROM TITLE through ending stillOPEN. All current jobs TERMINAL.

FOLLOWUP5770: Current actual main Prepared/PrideRock foreground retains visible Native samples despite MD foreground+MDterrain selection. Both are omitted from full-layout branch, equal map dimensions proven. See build/fidelity5769-foreground-gap-audit/report.json. Investigate original PlaneA initialization, scroll and dynamic/live-map/lava updates before enabling complete grid; do not infer plane equivalence from decoded assets/dimensions. Main PrideC00549 versus summitC007DB remain separate recipes. No renderer fix delivered by this audit.

CURRENT4724 DELIVERY: Public installed-preview4712 /352 MD leaves/451 rows.
FIXED native giraffe head artwork/colors in King. New independent Frames and
Palette at graphics.sprites.animals.giraffes. Seven original standing/bend/flat
images paired directly through descriptors/streams: C07D93/MD0CE15A,
C07DE6/0CE1C2,C07E35/0CE23A,C07E78/0CE2B2,C07EBF/0CE30A,C07F12/0CE372,
C07F59/0CE3DA. Original bounds/anchors exact. Captured reciprocal C58D60/
C58D70 actor; static C58D80 only flat. Native OBJ5 initial/final fingerprints
are the existing verified rhino bank, but source choices independent. MD1 is
the original live prepared scene palette. Full MD uses exact source pixels/
colors; mixed artwork/palette uses reviewed spatial/nearest-color remaps.
Native timing/gameplay/collisions/placements/audio remain unchanged. Original
MD downward stream adds anticipation phases; not retimed in this art fix.

4709 proves all seven source images/stream pose sets; return-stream durations
exact. Actual original7608 B8E02/MDpalette1 captured by restoring original7061
save; no title/level1 replay. Current7800 C58D60/nativepalette5 verified.
4713 proves all previous1645 serialized images AND map rows, palettes/native
death bank and gameplay28 payload byte-exact. Seven MD images appended,1652
images/4805335 bytes/policy125/helper4711; every new raster source-byte exact.

Fresh full352/7800 fixture4714 guest/nativePPU equals prior public350 nearby
7800 hashes. Same-core old-renderer4715/current MD/LLE4716 preserve full outer
session/presentation histories; guest/nativePPU/fullPCM unchanged and visible
delta only head. Explicit native/mixed controls use identical native4 backends
in both renderers, isolated graphics controls only (outer history absent).
Actual prior/current paced Windows4720 VIEWED: MD head/colors match MD body;
endpoints equal own full-wrapper headless. No source-identity bypass/save
migration or actor/pose/RNG edits. Normal original suffix3000 fields4721 sees
standing+flat head families with ZERO giraffe fallback/sampler diagnostics.

SCOPE LIMIT: five intermediate bend drawings are exhaustively source/map
verified, NOT claimed exercised by normal route or actual window. Four ordinary
local movement/jump probes4717-4719 also retained standing head only; do not
repeat those probes or claim successful bend/contact-timing coverage. All seven
are mapped with the same owner/bank guard; no native timing change.4722 proves
giraffeMD/rhinoSNES independence in exact head bounds. Other visible C58C08 tail
pieces correctly change with rhino source; initial whole-picture equality
assertion was invalid, not a source coupling defect.

Actual Setup/Full Genesis CMD4724 preserves all448 old source choices and adds
parent/Frames/Palette:451 rows,352 supported MD leaves. All other assets/helpers/
settings hashes unchanged; automatic bounded fallback log has new build hash.
Previous ride-obstacle4700, flying4677/checkpoint4669/monkey4660, ride wrap/head,
transition/vine/audio fixes retained. Launch Play Full Genesis.cmd.

Reusable current full352:4714/before.state at7800;4721/after.state at10800 with
remaining-after.tape and exact original_cut_after in4721/report.json. Native4
isolated fixtures are NOT complete MD-source walkthrough checkpoints. Original
MD4708 retains full7608 state/reference. Normal route ends5991/218 HP6/lives8.
Next prioritize report4 Pumbaa normal catching/scoring/rewards; earlier catches
1/2 do not prove high-count rewards. Other pickups/menu/audio/ledge contexts,
remaining report6/gameplay and all28-report/fullMD source goal remain OPEN.
Final unchanged original Genesis TAS NOT RUN; broad goal ACTIVE. This turn
PROGRESS: seven source drawings/head colors delivered, no full-level/finalTAS
or zero-fallback completion claim.

CURRENT4705 DELIVERY: Public installed-preview4700 /350 MD leaves/448 rows.
FIXED missing MD ostrich-ride obstacle artwork (report6/source audit). Five
original constructor-proven images: groundC45A16/MD0D10A2; lower branch
C3B6F7/0CDFFA + collision drawingC3B756/0CE072; upper branchC3B77B/0CE09A +
collision drawingC3B7F2/0CE132. New independent Frames and Palette leaves at
graphics.sprites.world_objects.ride_obstacles. Native banks0/1/2 retain exact
native palette guards, including both proven OBJ1/2 phases; MD uses original
prepared/live scene colors. Full MD images/anchors/bounds, priority retained.
Mixed artwork/palette sources use original-palette nearest color remaps; full
MD uses exact original indices/colors. Gameplay/script/collision unchanged.

Branch identity resolved at submission: position=parent+5A, parent+56=child
7E draw, reciprocal parent/collision draw, descriptor/pose and original ROM
callback/image signatures. No pose whitelist or silent fallback suppression.
Native heap slot not assumed. New diagnostic captured_descriptor reports the
actual submitted owner separately from legacy raw actor_descriptor. IMPORTANT:
4693/4694 initially failed because they misread that raw ordinary-task field
for child draws. It was NOT a stale-owner renderer failure. Correct4701 checks
the captured descriptor. Extracting native4 also loses outer MD-core history,
so such fixtures are isolated graphics controls, not normal walkthrough proof.

Fresh full350 current7000 checkpoint4695 (one unchanged original prefix) and
same-core prior renderer4696 enable real complete-wrapper old/MD/LLE controls
4701. Source-off and mixed choices checked separately on identical native4
backends in both renderers; no source-identity bypass/save migration. Game/
nativePPU/fullPCM exact within each group; pixel delta only obstacles. Actual
old/new paced full-wrapper Windows4702 VIEWED: original MD branch/collision
art and colors, Simba/scene retained, endpoints match own headless controls.
Normal full-wrapper original suffix600 fields4703 observes all five poses,
1049 old unknown records to zero, no obstacle palette rejection; whole guest/
nativePPU/fullPCM/poll count exact. Actual/copied guard cases reject bad links,
descriptors, poses, ROM signatures and sizes. Ground is also semantically tested
in an offline copy; no actor/pose/RNG was injected into gameplay.

1645 installed images/4786807 bytes/policy124, helper4690.4692 proves all old
1640 serialized images AND map rows, palettes/native death bank and gameplay28
payload byte-exact. Only five original images appended, each decoded original
MD raster byte-exact. Real Setup/CMD4705 preserves all old445 choices and adds
parent+Frames+Palette (448 rows,350 supported MD leaves); every other asset/
helper/settings hash unchanged. Automatic bounded fallback log retained with
new build hash. Previous flying4677/checkpoint4669/monkey4660/ride wrap/head/
transition/vine/audio fixes retained. Launch Play Full Genesis.cmd.

Reusable full350 checkpoints:4695/before.state at7000;4703/md/after.state at
7600 with remaining-after.tape and original_cut_after in4703/report.json.
No from-title repeat needed for nearby checks. Original4685 has full7061 MD
reference restored from6976 without replaying level1. Original event-flag-to-
constructor equivalence remains OPEN separately; equal scripts do not prove
that mapping. Giraffe platform drawings C07D93/C07F59, pickup art, menu/debug,
audio and other reported contexts remain OPEN; report6 is still partial.
All28 reports/fullMD source goal and final unchanged Genesis TAS remain ACTIVE.
This turn PROGRESS: five real missing source pictures/ownership delivered;
no full-ride, whole-game, zero-fallback or finalTAS completion claim.

CURRENT4682 DELIVERY: Public installed-preview4677 /348 MD leaves/445 rows.
FIXED native colors on shared flying creatures. New independent palette leaf
under graphics.sprites.animals.flying_creatures.palette. Original five idle/
reaction/takeoff/flight streams cover ten EXACT shared anchored/indexed images,
verified4676 including otherwise-unobserved reaction poseC6FBBC/MD0CEA92.
Original durations/loop targets exact. Two native descriptorsC58814/C5881D use
common C2ECD2, MD B8CA6/19FB02. Five actual original takeoff captures prove
sprite palette0 and common nontransparent MD colors. Current native OBJ0 and
captured reciprocal descriptor/pose guards required. Applies by shared program,
not level allowlist. Native flashes/unknown poses retain their diagnostics.
No duplicate images, assets/helpers, gameplay, animation or audio changes.

4678 actual complete10168 native4 backend with histories, ordinary Start pause:
explicit SNES source equals old picture/guest/PCM, creature-MD with Simba-SNES
independent; MD AOT/LLE exact, whole guest/nativePPU/full mixed PCM unchanged.
Visible change confined to the actual creature piece. Actual old/new paced
Windows4679 VIEWED and endpoints match own headless. Normal unchanged original
input200 fields4680 exercises nine idle/takeoff/flight poses:117 old unknown
records become zero through verified shared-art MD color provider. Guest/PPU/
PCM/poll count identical. Tenth reaction pose source-proven; not claimed run.
No allKing/source/playtest/finalTAS completion claim. Other constructed sprites,
pickup pictures, menu/debug and audio/report gaps remain OPEN; broad goal ACTIVE.

Build correction: inherited resource compile commands referenced frozen4578
source, so maintained resource-level diagnostic calls and updated checkpoint
help had not reached previous packages. Current game-patches now regenerated
from maintained source and that generated resource file actually compiled.
Health-death patch anchor updated for checkpoint help, same existing source
leaf/behavior. Retains prepared-only sprite/HUD activation, RNG/native hooks.
Existing public4669 checkpoint renderer fix was already in the wide object.
No lost settings or source rows: all prior443 unchanged plus parent/palette.
Real Setup/Full Genesis CMD4682 verifies348 leaves445 rows, every asset/helper/
settings hash and automatic fallback-log build. Prior checkpoint4669, monkey
intro4660, transition4620, vine4598 and sound fixes retained. Launch Play Full
Genesis.cmd. This turn PROGRESS: real source gap and resource diagnostic build
path fixed/published; whole-game zero-fallback fidelity remains unproven.

CURRENT4674 DELIVERY: Public installed-preview4669 /347 MD leaves/443 rows.
FIXED shared checkpoint heads retaining SNES colors in King. Old semantic
classifier was explicitly Pride-only even for the common C5889A/C588A6 program.
Three original native/MD drawings are exact anchored indexed images4668;
actual King OBJ0 matches the existing native palette guard, and four original
MD King CRAM0 captures agree with installed checkpoint MD colors. Removed only
the level/scene allowlist. Reciprocal task/draw, descriptor/pose, exact original
ROM callback/table signatures, visible OAM and strict native palette preserved.
Existing independent checkpoint Frames/Palette choices apply across worlds.
No new artwork/helper/asset/node/schema, gameplay, timing or audio changes.
Mismatching palettes/flashes still reject/log; no all-adult-context claim.

4670 genuine full10040 paused King: MD AOT/LLE exact, native Palette old/new
exact; native Frames plus MD Palette matches fullMD because source images are
original-shared. Guest/nativePPU/fullPCM unchanged. Pixel change ONLY inside
individual checkpoint piece rectangles4673. Actual old/new Windows4671 VIEWED:
head coat changes to original MD colors, scene/SImba/HUD retained. Endpoint
matches own headless.4672 actual-owner and other-owner/hero offline tests,
corrupt descriptor/backlinks/pose/fixed and original-ROM tamper guards pass.
Real unpaused original-input10000..10120 guest/nativePPU/fullPCM unchanged;
72 checkpoint gap records become zero through successful MD sampling, not
log suppression. Other unknown sprite records remain honestly reported.

Normal original-input source audit4666 continues reusable10000 to Graveyard
13600, lives9/health6; current complete13600 save and exact remaining original
suffix retained. Not final full-game TAS. Flying creatures/constructed sprites/
pickups and two unclassified audio requests still require source review.
Background/foreground fallback records at just13416..13418 remain visible in
audit; no broad transition completion claim. All28 reports/fullMD source audit
and final unchanged Genesis TAS remain OPEN, broad goal ACTIVE.

Real Setup and Full Genesis CMD4674 verify delivery, unchanged347 choices/
443 rows, every asset/helper/settings hash and automatic fallback-log build.
Prior monkey intro4660, outgoing interlevel4620, vine order4598 and sound fixes
retained. Launch Play Full Genesis.cmd. This turn PROGRESS: real shared source
gap fixed and published; no broad whole-game or zero-fallback claim.

CURRENT4665 DELIVERY: Public installed-preview4660 /347 MD leaves/443 rows.
FIXED first monkey pose using native colors in fullMD King. Original native
C43DCC and MD0CEC52 have EXACT anchored/indexed pixels; earlier bounded scan
started43E00 and omitted the valid earlier pose. Original full5000 RAM+ROM
verification4659 and independent current10000 decode4658 agree. Genuine route
4656 logs27 visible C43DCC/C58BD8 records5940..6394. Existing strict actor/pose/
OBJ2/3 palette guards and independent monkey Palette source now include30 poses.
No new artwork/helper/asset/node/schema/animation/gameplay change. Native source
remains native; all other29 poses/fingerprints unchanged. Maintained generator
439 now verifies/includes missing earlier source instead of regenerating29.

4662 actual complete5940 snapshot +one ordinary Start pauses natural pose: MD
AOT/LLE exact, native source old/new exact, full mixed PCM/WRAM/nativePPU picture
unchanged. RGB difference fits ONLY individual C43DCC native piece rectangles
(upper visible monkey), not merely a broad actor bounding-box union. Native
source control preserves complete native4 backend histories; no downgrade or
old-save migration. Actual old/new Windows4663 VIEWED, endpoints match respective
headless. Complete current saves still accepted because choices/schema unchanged.
Also calibrates fallback diagnostics for369 already-proven shared monkey/tail
draws: exact indexed aliases plus successful strict MD coat colors count as MD,
not unclassified native storage. Failed/unknown poses/owners/palettes still log.
Successful specialized MD checkpoint samples are likewise labeled accurately.
CORRECTION to4653 research inference: C58814/C6FB59 is a flying creature, not
a checkpoint (original566/MD19FB02); that success flag never matched those King
draws. They still log in4656. Common C5889A checkpoint coverage, flying creatures,
world/constructed/pickup source paths remain OPEN for actual source verification.
King original-input audit4656 now has genuine reusable10000 checkpoint with
remaining original input suffix; remaining King-to-Graveyard audit continues.
This is NOT complete King/source/playtest or final whole-game TAS proof.

Same347 leaves443 rows/settings/assets/helpers; existing automatic bounded
fallback JSONL and prior first-level transition4620/vine4598/audio fixes retained.
Real Setup/Full Genesis CMD4665 verifies delivery/log build hash. All remaining
reported/source gaps and final unchanged original Genesis TAS remain OPEN;
broad goal ACTIVE. Launch Play Full Genesis.cmd.

CURRENT4643 DELIVERY: Public installed-preview4637 /347 MD leaves/443 rows.
User requested EVERY Sega fallback logged. Play Full Genesis.cmd now enables
build/logs/full-genesis-fallbacks.jsonl automatically, build hash included.
Four rotating segments near8MiB each, no recordings/ROM/image/audio payloads.
Frame/level/scene/source/reason/actor/pose-or-caller/detail/count JSONL; repeated
frames counted, same-frame visits aggregated,2048-table overflow batches without
loss. Frame heartbeats distinguish active logging from no file. Explicit SNES
choices valid; no game/input/CPU/PPU/audio/source behavior change or crash/mute.
See docs/fallback-logging.md and tools/summarize_fallback_log.py.

Separate kinds: fallback (native compositor pixel survives failed MD source),
sampling_failure (may be offscreen/flash), unclassified sprite/canvas/audio
(native path needs source/visibility/voice-owner review), coverage_gap (currently
unsupported MD leaf inventory). Known complete MD host canvases resolve ONLY
same-frame visible underlay candidates; do not accuse valid MD overlays. Shared
original pixels/silence and native implementation details need semantic review,
not blanket replacement. Empty bounded log is NOT complete no-fallback proof.
Three unsupported audio Other leaf categories explicitly reported at startup.
Genuine full King5800->5920 original route logs373 unclassified sprite records
(monkeys/constructed roles etc), not yet proven bugs. Follow this evidence, not
an assumption that every native callback means an audible/visible SNES leak.

Unit4636: escaping, repeated frames,3000-event overflow, four-file4096-test
rotation/totals, same-frame-only canvas resolution, disabled/failed-open pass.
Current complete4288 scene4638: old4620/candidate logging off/on and MD AOT-LLE
WRAM/nativePPU picture/final PNG/full PCM EXACT; diagnostic event/frame records
AOT-LLE exact excluding PID/time/header. Explicit native graphics/audio controls
retain picture/PCM and log zero fallback events. Genuine complete King4639 same
WRAM/nativePPU picture/displayed PNG/PCM as public4620. Actual paced Windows4640
VIEWED normal gameplay while logging,59.75fps/no late resyncs, endpoint matches
headless. Maintained game-patches apply to ignored copies4644; runtime/tests/
preparer CMake link standalone logger. Installed helpers/assets UNCHANGED.
Audio compiles exact public4577 plus diagnostics, private4404 still excluded.
Same347 leaves443 rows/settings/assets/helpers/schema; prior first-level flash
4620, vine ordering4598, shared1UP/global Continue and all earlier fixes retained.
Actual Setup/Full Genesis CMD4643 verifies tree and default live log build hash.
Remaining28-report/source/asset gaps and final unchanged original Genesis TAS
remain OPEN; broad goal ACTIVE. This delivers instrumentation, not zero-fallback
fidelity or full-playtest completion.

CURRENT4627 DELIVERY: Public installed-preview4620 /347 MD leaves/443 rows.
Launch Play Full Genesis.cmd. FIXED reported SNES image after first-level MD
scripted scene. Old MD fade reaches black, then full-bright SNES cliff/sun
illustration returns and fades twice. Fresh current4598 original credited
route4607; current4100 checkpoint, exact nearby replay4614; read-only final
canvas observer4610 neutral through5800. End4396; old C005AB persists despite
next level tag, then descriptor000000 is uninitialized teardown, not handoff.
New selected MD completed-black ownership ends once at actual valid next scene
C005DD4427. No guest/PPU/input/audio timing or source planes changed. Existing
short interlevel-save restriction extends through owned teardown; no new save
format/migration. Rejected first candidate4612/4616 left3 flash frames in zero
descriptor gap; NEVER PUBLISHED. Final4620/4623 checks101 full composed frames:
exactly28 visible native-art frames4397..4425 corrected; all active MD fade
frames and every other captured frame exact.4621 selected AOT/LLE, explicit
native interlevel source, ordinary no-Start natural exit, WRAM/native PPU
picture and full mixed PCM controls pass; bonus scene/result picture unchanged.
Actual old/new paced Windows4625 VIEWED:4397..4414 native art versus black;
subsequent4960 bonus result retained, final5000 matches respective headless.
Current4288 complete checkpoint4624 now enables fast nearby transition checks
without replaying level. Preserve original remaining tape cut3912. This fixture
is current and untouched original input, not a migrated old development save.
Same347 MD leaves443 rows/settings/all installed assets/helpers; public4598
vine-order compositor, shared1UP/global Continue audio and prior fixes retained.
Real Setup/Full Genesis CMD4627 verifies delivery. Specific first-level outgoing
native-image report FIXED; report13 other transitions, other open sprite/sound/
grab/source contexts and final unchanged full Genesis TAS remain OPEN. Broad
goal ACTIVE. No complete-playtest or final-TAS claim.

CURRENT4466 King normal hippo-stack foreground: original live Plane A E00064x32 at2842/153, source4456. All1189 visible/edge tile names (priority/palette/flip) and every used tile equal original authored map4458. Full normal King correspondence4459:12391/12400 cells have exact four names;9 fall back to native, including visible hippo face/ledge cells3008/352,3136/352,3024/368,3152/368. Complete original map selected only with MD King terrain and MD foreground. Ride512 streaming branch retains precedence and its actual user output is pixel/guest-exact4465. Native foreground/terrain controls4463 exact; old/new actual Windows4464 VIEWED. No source plane or scroll rule generalized to other scenes; background Plane B unchanged. Delivered4462; remaining other reports/TAS open.

CURRENT4276 Return full foreground delivered4271: normal4400x688 MD grid
selected with MD Return terrain + MD foreground. Original Plane A E00064x32
ring names incl.priority/palette/flip and every used tile match five actual
VDP states4268 (1189 names each), displayed FC00 A X/VSRAM A Y, origin0. Existing
independent Plane B112/39/73 bands888 unchanged. No live map mutations in current
late Return4269. Actual old/new Windows4273 VIEWED, source-off/AOT-LLE4272; all
prepared caches unchanged4275. Details: [Return audit](return-foreground-and-grab-audit.md).
No source plane correspondence/edge/wrap/clock rule generalized to other levels.

CURRENT4237 Sound Test delivered4230: independent MD picker uses the original
title two-plane backdrop/footer/body/copyright4215/4217, without Options labels.
Installer menu-v7 appends that exact72000-byte source record; all older backdrop
payloads unchanged. Runtime seven circular song rows and selector rendered from
installed font/palette, not guest screenshot data. Final actual Windows entry/
changed-selection4232 VIEWED. No world layer/scroll/edge rule changed. Title/
ordinary Options sources remain independent. Debug/returned-title contexts open.

CURRENT4219 Sound Test SOURCE ONLY: Original4215 retains the reviewed title
two-plane backdrop,footer28EA52,copyright290C62 andbody29F5EA; replaces Options
labels with seven song sprites28F62C..28F83C andselector28FA92. Original VDP
two full indexed captures exactly reconstructed4217 from ROM-prepared backdrop
and existing installed font/palette. This is not proof of a current native
scene renderer: public4205 still shows native SoundTest4218. No layer/scroll
rule broadened or world recipe changed. Runtime source/context wiring pending.

CURRENT4214 publisher-card scene: original startup29F6BA/291372 uploads one
64x32 Plane A atE000 from maps29FB98/2947D4/294B0A. Plane B C000 cleared;
H-scroll FC00 wordsA/B zero,full-plane H/V modes,VS-A/B zero; backdrop0 black,
transparent tile0,SAT entry0 allzero/terminating/offscreen verified actual three
contexts4201/4202/4212. Three source tile/map/palette recipes and original SEGA
palette cycle are prepared in menu-v6 TLKPUB01; no emulator images used as data.
Native runtime paints selected cold-start owned level14/C0057B/C462F6 phases;
no claim SNES and MD plane correspondence/repeating edges. Same original320
canvas,central32 crop for256 view; actual320 Windows4210 all3 cards VIEWED.
Native actor clock adds189-count SEGA prefix,keeps subsequent native card hold/
blank phases; original total startup fade/timing NOT claimed. Current native
choice whole guest/window/PCM exact4178. Decoded source proof and actual runtime
ownership/window qualification are separate. No world-background recipe changed.

CURRENT4174 adult death presentation: body-only repair, no new background recipe.
Natural maul/death4160/4161 retains level9/descriptorC00549, ageFFFF/HP0,
actionC37E76. Actual all visible lines in source capture are non-stage mode1,
OBJ main10/sub0, no BG layers enabled; BG map/scroll registers retain prior
level data and are NOT evidence to render an underlying level here. Native
C089B7/C089EE..C08A02 loads adult E6BF99 into7F0000,10752 bytes; digest and actual
loaded bank verified4161. MD adult death animation pointer07E572 ->07E57A,
13 tokens/12 original drawings/loop, shared indexed art/anchors. Original MD
death-background initialization/planes are not newly audited or substituted:
the existing native black stock canvas/HUD remains byte-identical outside
Simba. Only selected body art/color is sampled after that copy, under exact
adult scene/action/bank and per-line mode/OBJ/windows/math guards. No plane
correspondence, repeating-edge rule, scroll or level-map reuse assumption.
Early/mid/late native-palette controls exact4165; real old/new Windows4171 VIEWED.

CURRENT3926: Options original two-plane settings scene is delivered in3919.
Menu-v4 contains its prepared original plane/logo/font/copyright/selector data;
actual MD/native Windows Exit3921 and public MD Options3925 VIEWED. Native-source
extra Exit uses decoded native BG3 font, not MD art. Popup ownership A68E rejects
debug overlays; opening/audition/debug presentation remains separate pending work.

CURRENT3912: Original Options retains the same two original title planes, zero
scroll and palette, plus separate labels/settings sprites. Native prepared-data
Options renderer3911 matches17 actual original VDP contexts. No public Options
renderer/host ownership claim yet. Public ready-title3902 is unchanged.

CURRENT3909: MD ready-title is a separate two-plane scene, not level0 scenery.
Original initializer29575A, tile295864, planeB299414 atC000, planeA2990EA atE000,
64x32, zero scroll, palette2999EE. Logo/Simba/text are separately sourced sprites.
Native renderer and original VDP submissions match3900; actual Windows3906 and
public3908 VIEWED. Opening animation/Options still native. See current HANDOFF.

CURRENT3870: Public3861 restores original MD Stampede question marker and fifteen observed main-scene cub animation gaps; shared main-level pickup sounds retained. Actual Setup3868 and real window3869 checked. All other open reports, complete source audit and final unchanged original Genesis TAS remain pending. See docs/HANDOFF.md. Earlier entries below are historical.

CURRENT3833: Public3825 repairs actual interlevel controller-bank sampling; original-input King traversal with8 lives verified. Expanded Full MD sprite/sound audit and all28 reports remain active. Partial3822/3834 expose more gaps and a later walkthrough failure. No full-game completion claim. See docs/HANDOFF.md and docs/full-md-source-audit.md. Earlier entries below are historical.

CURRENT3818: Public3813 restores the missing original MD panther terminal combat pose (report23). Qualification3816/publication3817, helper3812/policy109/schema28/1496 images,326 MD leaves. Settings and other assets unchanged; no background recipe change. Remaining reports/final original Genesis TAS open. See docs/HANDOFF.md. Earlier entries below are historical.

CURRENT3807: Public3802 adds independently selected MD Rafiki arena gate sound (report24). Qualification3805/publication3806,326 MD leaves, assets/settings unchanged; no background recipe change. Remaining reports and final original Genesis TAS open. See docs/destiny-gate-sound.md and docs/HANDOFF.md. Earlier entries below are historical.

CURRENT3791: Public installed-preview3786 delivers stable selected King animal palettes and original MD hippo artwork/anchors/palette/placement. Actual Setup and Full Genesis CMD verified3790;325 MD leaves selected, settings and all other prepared assets preserved. Helper3775/policy108/schema28,1495 images/4423671 bytes; view9/audio5. Reports6/7 have concrete fixes; other reports and final unchanged original Genesis TAS remain open. See docs/HANDOFF.md and docs/user-playtest-bugs.md. Earlier entries below are historical.

REVIEW3751 / public still3731: Active goal covers all28 user reports; no new
binary in this review. Reports4 and5 now have concrete normal-play evidence.
Bug Toss:3738 ordinary39 RIGHT reads after the genuine first catch reaches
Pumbaa X286 and catches the X288 bug at1942. Result card ends with count/display2.
3748 compares old3716/current3731 at1930: same player286/214; old submits0 Pumbaa
pieces and0 right-bug pieces, current submits7 and1. Real Windows3739 at1920..1933
VIEWED. The shared3731 fixed320 draw-bound correction therefore repairs the
wider-arena playability problem as well as Timon's thrower visibility. Movement
and catches themselves were already running while those actors were invisible.
CORRECTION to3737 notes: result trace begin count0 is the animated display's
initial value, NOT a lost catch.3729 ends at1;3738 ends at2. Actual player counter
B231 changes at1870/1942. Do not chase a nonexistent scoring fault from begin0.
No21-catch/reward-cycle or newly complete bonus-audio claim is made.
Rhino:3745 idle203 owner records and3746 ordinary bounce121 records cover all13
mapped native poses with0 rejected owners and0 palette fallbacks.3750 uses the
real submitted/live-pose disagreement at5195: old3650 visibly swaps to native
head, current keeps selected MD art. Same player/camera; changed image bounds
156,282..268,414. Before/after VIEWED. Actual Windows3747 bounce5194..5203 VIEWED;
final window/reference guest state and picture match. Existing3692 captured-owner
fix addresses report5 too. Stop repeating these checks without a new failure.
Remaining work: report6 ostrich ride,7 hippo ledges,1 menu source,9 jump voice,
10 bones, remaining sprites/geometry/grab reports,20 source sounds,24 gate sound,
26 monkeys/obstacles,27 chasing boulder; finish entry/transition/encounter coverage
on partial reports. Final original Genesis TAS remains pending after fixes.
King evidence:3742 verifies original400x31 MD/native grids. Only9 static cells
differ in opacity (433 pixels); do not assume this explains the whole ride.
3744 retains genuine supported renderer/palette histories from old nearby rides
and a later tree section (fixture labelled hippo is actually player5914 near
late monkeys, not the user's opening hippo screenshot).3740 stripped renderer
history and produced artificial blue late-ride colors; do not fix runtime from
that fixture. Raw research version3 can retain the supported TLKVIEW history
while stripping only old audio, with guest state unchanged. No migration added.
3743 is one fresh current unchanged from-title input PREFIX to8500 (poll7403),
level1,7 spare lives, palette transition complete. Useful initialization evidence,
NOT a final TAS gate or proof of desync from life count alone.3741's older entry
suffix is also observation only. No King renderer change has been made yet.

CURRENT3721: Public installed-preview3716 / maintained3716 retains3692 music/
interlevel/owner fixes and3703 Hakuna/Destiny geometry, and adds complete Hunt
foregrounds plus descriptor-owned outgoing world presentation. Original Hunt
maps require prepared MD Y-origin16 (extra top row); their normalized floor/tag
grids are identical.3710 ordinary practice13 reproduces the broken branch.
3713 complete-map rendering removes its tile splices; guest WRAM/background
camera and native-foreground source-off pictures unchanged. No new layer or
background scroll recipe. Existing helper3612/policy107/schema28 assets retained.
3714 normal idle Hunt exit assigns next-main0 at3281 while descriptorC00673
remains displayed through3292. DisplaySceneContext normalizes ONLY the renderer
RAM snapshot from verified ROM world descriptors0..13, before map detection.
Guest RAM/input/AI unchanged.3719 completes real Windows3718 checks:12 owner
corrections, full guest WRAM/final picture equality and pixel-identical explicit
all-SNES graphics control. Failed3718 control left inherited graphics MD under
game=md; do not mistake replacing explicit leaves alone for a native profile.
Actual bright/outgoing Windows images VIEWED.3720 qualifies;3721 publishes
exact binary/root metadata and actual CMD/all322 MD choices; settings unchanged.
Audio history5/view history9 unchanged. Full original Genesis TAS still pending
after remaining visible fixes;3654 remains old-build walkthrough evidence only.
USER CLARIFICATION: Pumbaa Bug Toss defect is MOVEMENT/CATCHING, not artwork.
User also reports Timon disappearing at edges in the same bonus context (new28).
Next prioritize normal Toss controls/catches and thrower edge visibility; the
zero-catch TAS path is insufficient. Existing MD arena224->288 and falling-bug
cull255->319 are implemented, but generic draw culling still requires optional
s_spawn_lead and may use a different viewport origin than fixed320 Toss.
Confirm with real actors/draw records; preserve ordinary input and source choices.
All other open reports remain tracked. No hyena sound fix was made: existing
regular-jump silence audit is historical, user9 needs actual post-skull evidence.
The first later-slope fixture3138 uses actorB893 (inside the current voice pool
guard); do not blame the c213 limit without a live rejected owner observation.
See [user playtest defects](user-playtest-bugs.md).

CURRENT3708: Public installed-preview3703 / maintained3703 adds the original
MD Hakuna/Destiny foreground layouts when BOTH MD foreground artwork and the
matching MD terrain choice are selected. Prior native-cell correspondence kept
SNES opacity while gameplay used MD floors:993 Hakuna /946 Destiny cells have
different visible shapes.3701 independently verifies both prepared maps against
ROMs and exact225x71 /302x44 world grids. Finite foreground origins/dimensions
are matched; background layer/scroll/initialization recipes are unchanged.
3704 nearby ledge/gap checks: gameplay WRAM/input unchanged, SNES-terrain
source-off pictures unchanged, selected AOT/LLE equal.3705 actual Windows both
scenes VIEWED, full WRAM/picture match headless.3706 original MD confirms the
nearby hanging animation itself: do not �repair� an intended pose by guessing.
Separate reported grip offsets/adult sprite corruption remain to reproduce.
3707 qualification;3708 actual Full Genesis CMD/all322 MD choices publication.
Retains3692 music/interlevel/captured-owner fixes. Helper3612/policy107/schema28,
1482 images, audio history5/view history9 and prepared assets/settings unchanged.
Other user reports remain OPEN. Final original Genesis TAS pending after fixes;
3654 is old-build walkthrough evidence only. Next: bonus/Hunt scene ownership,
ostrich/hippo presentation, reported sprite/contact locations and missing sounds.
See [user playtest defects](user-playtest-bugs.md).

CURRENT3605: Maintained3598 / isolated installed3599; helper3588,
policy106/schema27/TLKNXT09,4,405,071 bytes/1482 images; wide history8.
Rain art/color gap IMPLEMENTED under EXISTING world-object frames/palette
choices. Original3584/3585 verifies MD17A444 against actual SAT tile0480,
palette0, and native C2F33E RAM bitmap. No guessed adjacent weather pairing.
One5x5 image adds37 bytes; ALL earlier1481 image records and entire gameplay
payload are byte-identical. Full catalog regenerated through existing tool.
Native C585D0 fixed draw records retain validated ordinary actor links;
renderer classifies them as weather rather than HUD. First candidates3589/3592
did not reach the fixed-object path; failed checks3590/3593 are retained.
3596 then exposed prior HUD recoloring of native rain.3597 verifies corrected
native palette control, four distinct independent art/color combinations,
selected compiled/interpreted equality and identical entire guest WRAM.
MD particles use the scene's live bank0 colors through the existing rain fade,
independently of scenery source. No gameplay/RNG/input changes or new toggle.
Actual isolated Setup3599 and installed Windows3600 PASS; actual60030..60042
VIEWED, blue MD rain, headless/window WRAM and picture agree. All319 supported
MD leaves enabled3601. Root settings/data/shared2687 launchers unchanged.
LIFE GAP NOW LOCATED: original TAS gains raw8->9 lives at original29317,
Hakuna Simba2475/310, research input27156. Prior valid native full gate3487
at matched input/nativefield29862 stays7 spare lives: missing one reward.
Original3602 from nearby20500 save through41000 and audit3603 locate this
without a new full native replay. Native three Hakuna deaths are real events;
identify the actual source reward/pickup and implement its rule/placement,
not a compensating life. Original3602 CSV health column mistakenly reads
CCF0, not established health; this column is NOT used in the life conclusion.
Next: Hakuna missing reward; remaining native/capability scope audit; final
installed ORIGINAL Genesis TAS from title through credits, then public delivery.
Prior installed3478/report3487 full pass remains valid; current3599 final gate
NOT YET RUN. Overall goal ACTIVE. No older-build save compatibility work.
See [postfight scenery](summit-postfight-scenery.md) and [completion audit](final-fidelity-completion-audit.md).

CURRENT3583: Maintained3576 / isolated installed3579; helper3565,
policy105/schema27/TLKNXT09,4,405,034 bytes/1481 images; wide history8.
IMPLEMENTED original postfight foreground/background and rain palette under
EXISTING independent scenery choices. Native C00549/C007DB descriptors use
identical gfx/map/blocks; original3553/3555 inherited E000/C000 planes/scroll
already source verified. Renderer requires prepared rain target before enabling
postfight scenery; unknown/unsupported contexts retain explicit native fallback.
Data appends64 colors from08E6B8 after occupied2368 slots (new WORDS2432),
with pure native3-bit channel-step API.3566 actual helper import/API matches
all seven observed original64-color steps; all1481 image records/old palette
banks and12 other gameplay sections BYTE IDENTICAL. Only128-byte target plus
version/policy metadata changed; no original ROM code read for this at runtime.
Source-event correction: first3567 used early A6C2 weather flag, ~200 updates
too early.3576 uses actual Simba phase11, as MD1B2C6C writes E9CE=1 AFTER
phase10 hold. Do NOT use first installed3572 as current. New3577 rain starts
59666/phase11, first source step59668, then every9 actual scene updates through
59722/step7. Normal lightning base retained in saved phase; no guest/RNG/input
writes, extra action timers, original emulator fallback or forced field equality.
First3568 test assumed raw NMI fields; actual native16-field lag retains same
latch.3569 checked real scene updates instead, no lag/pause polish was made.
3577 old/new SNES entire WRAM/picture equal; MD compiled/interpreted equal;
graphics choices leave guest WRAM unchanged.3570 checks eight short independent
art/color combinations on same prepared data. Current terminal image is exactly
the same as first3567; only the rain START event changed. No mixed-grid replay.
3578 CURRENT same-build frontend59680->59690 mid-fade save
matches uninterrupted entire WRAM/picture/base/step/delay. History8 validates
encoded rain state; no stale-build migration or compatibility work added.
3579 actual isolated Setup/startup PASS, root settings/data/shared2687 untouched.
3580 installed all-MD actual Windows60030..60036 VIEWED, whole WRAM/picture
matches headless; no new sound/video recordings.3581 ALL319 compiled-supported
MD leaves actually resolve MD, including score, voices and scenery. No available
MD leaf disabled. This is NOT the final installed from-title TAS gate yet.
REMAINING CONCRETE: installed rain contains native palette0 particles. Scene
JSON identifies C585D0/poseC2F33E, fixed screen16-size pieces; pose absent from
prepared sprite map and current later-world owner guard. Original MD59000 rain
is blue/white. Review actual original draw owner/pose/palette, then implement
under existing world-object art/palette choices; do not call plane proof a
complete weather-sprite renderer. No guessed C67DEF/MD1B2D4E actor pairing.
3582 reads EXISTING original snapshots and prior valid from-title3487 progress,
not a new replay: Stampede19900 expected visible8/native8; by Destiny41000
expected MD7/native6 at matching original input37945, same stage. Delta persists
through final original57325/input52909. Trace the ACTUAL first reward/pickup/
death difference between those checkpoints; do NOT alter starting resources or
grant a compensating life. No manufactured pass. Original MD raw counter includes
current life (displayraw-1), native counter directly means spare lives.
After these concrete weather/life checks, audit remaining explicitly native
scopes, then final installed original TAS/title-to-credits and public delivery.
Prior3487 full gate PASS remains valid on3478; goal ACTIVE, not complete.
See [postfight scenery](summit-postfight-scenery.md) and [completion audit](final-fidelity-completion-audit.md).

CURRENT3563: Maintained3561 (camera3559 + catalog text), latest isolated
installed3501 unchanged. Existing gameplay.camera now remains active in actual
Pride Rock postfight C007DB. It had reverted to SNES arithmetic at that descriptor.
Original MD stable camera486/16 for Simba678/134 vs native502/16: reuse existing
MD320 lead window192, no hardcoded camera/player position or pixel shift.
3560 nearby genuine58620->59200: selected camera486/storedY15 (logical16),
native502/15. Old3544/new SNES whole WRAM/image/state exactly agree; selected
compiled/interpreted agree; player678/134/HP10/lives6 unchanged,0 gameplay
words remain.3561 help text accurately includes postfight;3562 real Windows
59100..59112 VIEWED, whole WRAM/picture match. No new camera micro-toggle.
SCENERY SOURCE3553: original unmodified movie57000->60000, 3001 per-frame
palette/camera rows, seven full plane snapshots; observed initialization helper
hooks do NOT fire.3555 compares inherited MD9 finite world map/blocks/tiles
with actual streamed E000 foreground: ALL501760 pixel tokens exact, including
summit, camera relocation and stable postfight.3550 backgroundC000/used tiles/
96/88/40 scroll reuse remains. Neither proof enables a renderer by itself.
CRITICAL PALETTE3556/3557: MD stops normal three-palette lightning when E9CE
starts. At58450/script3, then EVERY9 updates through58504/script57, seven
one-unit3-bit channel steps reach separate targetROM08E6B8. All64 colors at
each actual transition exactly match native-source formula18D7B0. Current
prepared data has ONLY08E538/08E5B8/08E638; target08E6B8 is MISSING.
Thus do not simply enable normal phase cycling in postfight or claim full MD
scenery. No runtime scenery/capability expansion made yet; native fallback
still accurate. Both foreground/background geometry can reuse existing assets;
prepare the extra target and source-correct fading before renderer integration.
SOURCE LABEL CAUTION:3552 postfight-frame.txt is actually QUEUED sunrise
initializer1CDD3A (loads29585C,2990EA/299414, clearsC60C), NOT executing
postfight each frame. CCC0 points to next initializer.3554 native-weather.txt
C67DEF is an ember/fire owner, not established as MD palette-controller pair;
do NOT infer correspondence from the nearby MD1B2D4E listing. Palette source
08E4C6..08E530 /18D7B0 and actual CRAM are the authoritative rain evidence.
NEXT IMPLEMENT: append rain target to installer-owned next-scene colors (current
WORDS2368 slots fully occupied; add64 at end, version TLKNXT08->09, fresh data/
policy/schema as required). Do not overwrite native bank or bonus palettes.
Add data API, then independent scenery colors/foreground/background integration
for postfight; preserve existing saved pause-aware scene palette state. Check
its history serialization/phase validators before choosing new rain-state bits.
Original fade is MD3-bit channel +/-1 then existing RGB555 quantization, not
linear RGB555 increments. MD camera now supplies proper composition. Review
associated weather/scene actors' meaningful timing when integrating; Simba
holds already3544. Then final actual Setup/all-MD resolution/Windows/full
original TAS/public delivery remain. Public/shared2687, root settings/data and
helper3450/policy104/schema26/1481 images unchanged.3487 full from-title TAS
PASS valid on installed3478, not final gate for3561. Goal ACTIVE.
See [summit/postfight scenery](summit-postfight-scenery.md) and [completion audit](final-fidelity-completion-audit.md).

Current cliff scene delivery3414: [prepared source planes and native playback](post-stampede-cliff-work.md).
Original1CAD9C fixed E000/C000,64x32,zero scroll/SATF800:3397 rebuilds actual
initialized maps from ROM20DDFA/203092+160/206372 and20E2B0 tiles;3399 prepares
these with13E04C actor bank/212A26 palette.3401 first drawing verified through
shared RGB555.3410 installed actual Windows cliff inspected. Natural sequence
344 updates independently checked; no repeating-edge assumption or cross-console
plane pairing. Mixed SNES art under MD timing remains explicit black backdrop.
Earlier normal-scene evidence below retains its stated scope.

Current public Windows build is **1807**, actual Setup/publication1813.
Launch `Play Available MD.cmd`, or `Play Stampede MD.cmd` for direct level3 entry.
Player SHA256 `14790306ff8ffcd9383bbae159529541d2682a34df7dcfd8b3243f714a2cc081`.
Helper1806 / sprite-v2 **policy43**, cache3,946,305 bytes. Scene787 /scene-v3,
gameplay aggregate schema7/ten sections unchanged. Settings/older payloads preserved.

Stampede now has the source-verified original MD canyon through the existing
**Graphics > Scenery > Background** choice. Its **Stampede canyon colors** choice
remains independent. MD geometry with SNES colors uses the nearest original
native palette mapping; it does not claim original SNES geometry. SNES background
still uses native perspective. H32 native256 viewport remains deliberate.
Prepared TLKNXT06 adds TLKSTD01:three256x224 color-index/priority images. Setup
uses decoded1C6F5C tiles,1C9F7C map, explicit FF tile1023/83FF matte initialization,
128x32 shared plane map, three planeA pages and fixed planeB fourth page. There
is no normal-scene descriptor guess or runtime ROM-code/data decompression.
Original colors, other9 aggregate records and all sprite images remain unchanged.

Runtime phase is (saved native scheduler0A40/5)%3. Native C43277 resets the clock;
C0FA58 increments it with ordinary scene updates. No wall clock, extra render
counter, guest writes or new save schema is needed. Rendering a native restored
checkpoint therefore continues the same phase as uninterrupted execution.
Stampede native HUD bank7C93 differs from shared cub7B93. Its actual bank now
activates the existing MD health/life frame adapter and separate MD HUD palette;
original MD high sprite priority is retained above the canyon matte. Health-only
stage does not gain an invented roar meter. This is limited to exact Stampede
scene/C0041D and matching native palette. Other palettes retain native handling.

1804 original source proof:162288 visible background pixels agree at three phases.
1808 actual installer proof:all172032 prepared tokens exact.1811 final local stage3
fixture: prior1797/new source-off background+HUD SNES full WRAM/picture identical;
selected AOT/LLE/real Windows pictures and full WRAM match. Graphics/palette choices
leave guest state unchanged. A restored native checkpoint matches continuous2371
full WRAM/picture; real2340 client plus native-color control visually inspected.
The existing frontend-wrapped stage save was rejected by source-choice validation;
proof explicitly extracts its unchanged native payload. Do not advertise frontend
save compatibility from this check or add old-development-save migration work.
1812 bounded qualification,1813 actual Setup/installed startup/publication PASS.
Sources/previous launcher/helper/manifest preserved in registered1805 baseline.
No framework/generated code edits, recordings, unrelated suites or whole-game rerun.

**All-level MD fidelity and final installed unchanged Genesis TAS remain ACTIVE /
INCOMPLETE.** This delivers Stampede canyon presentation, not a complete MD stage
controller, obstacle schedule or walkthrough. Next implement independently selected
actual Stampede movement bounds (MD left40 vs native32) and review its obstacle
schedule/contact rules from the original source; retain native geometry/sprite
behavior unless a visible difference is evidenced. The six later normal-stage
entry choices1797 remain. Adult/Scar/remaining bonus/ending scope and the known
Graveyard original TAS failure remain open. Do not alter gameplay inputs, force
RNG or claim the final installed original TAS passed. Use nearby fixtures:
`build/fidelity1803-stampede-source/native/ready.state` at2300; native playerB293,
not B213. Current final delivery is `build/fidelity1811-stampede-delivery`; old
1809/1810 are intermediate diagnostics, not the final build proof. Earlier notes
below are historical and superseded by this entry.

Stampede follow-up1803/1804 (research; public build1797 unchanged): actual original
TAS transition19306 resumed only through20500. Stage initializer1B550A explicitly
sets Simba128/182 at1B5554, confirmed live1A4896 at19349; generic descriptor100/0
is unused. Do not add an incorrect MD entry-position override for Stampede.

The original canyon is now source-verified: 1B5178 selects H32,128x32 tilemap,
both plane bases8000, full-plane scrolling.1C6F5C decodes24736 tile bytes toVRAM0;
explicit FF tile1023 supplies opaque matte. The map fills83FF then1C9F7C decodes
5120 bytes at8300. Palette1CAC22 is128 bytes. PlaneA cycles0/-256/-512 every5
controller updates (1B56F6); planeB remains+256, sampling a fixed fourth page.
This is a three-frame prepared canyon plus fixed backdrop, not a generic normal
scrolling scene or guessed per-line deformation.1804 reconstructs source tiles,
map and palette exactly at19800/20000/20500 and matches162288 visible background
pixels, zero mismatches, excluding linked SAT sprite rectangles. Original screenshot
has14px/8px core overscan border, not game-world offsets. Each game view is256x224.

Next implement this recipe in the native installation preparer and independent
background runtime, with explicit phase/reset/restart/save handling and honest
availability. Do not claim renderer delivery from this source proof. Existing
public capability still correctly says native Stampede perspective with MD colors.
Keep background/palette/sprites independent, native fallback accurate; verify
actual Windows output and focused source-off/AOT/LLE checks after integration.
MD controls also limit left movement at40 (native32), while speed3/floor182/
jump initial-5/six-update ascent delay agree in reviewed handlers. Treat the
boundary as a separate source choice rather than mixing it into graphics.

Read-only native practice3 fixture is
build/fidelity1803-stampede-source/native/ready.state at2300; its pre-entry save
is in the same folder. Native Stampede Simba is actorB293/C5858A, not B213;
normal-player log zeros are not a player-position failure. MD transition and three
nearby source saves are in1803. See build/fidelity1804-stampede-planes/report.json
and tools/check_fidelity1804_stampede_planes.py for recipe and bounded proof.
No engine/runtime changes, recordings or public republishing this increment.
The full MD scope and original installed Genesis TAS remain ACTIVE/INCOMPLETE;
the known Graveyard route failure is not resolved by this source work.

Public1636 adds independent original MD credits text with SpritePreparer1629 /
sprite-v2 policy33. Original1627 separately observes credits initialization:
37 glyph tiles from1CFB98 at VRAM0, map1CEF78 streamed40 columns at planeA/E000,
palette1CFD34, blank planeB, zero horizontal/line scroll, one vertical pixel per
three updates. The64-column/32-row VRAM ring is storage, not repeating content.
At the final blank source row the map pointer stops while the ring keeps moving.
1632 six actual compositions from first rows through final content match after
retained RGB expansion normalization. Prepared TLKCRD01 includes the decoded font,
260-row map and palette; playback uses bounded content and never repeats edges.
256 viewport is a centered crop of the320 layout. Native final hold/fade/exit
remain; no other postfight/background capability follows. See
[ending scope and delivery evidence](ending-sunrise.md). Older entries are history.

Public1619 adds the original static title actor over the ending sunrise, with
SpritePreparer1618 / sprite-v2 policy32. Original1613 captures before/after its
actual1CDEA0 creation, and1621 checks three complete post-title compositions.
The existing two fixed64x32 planes (A/E000, B/C000), zero VSRAM/line/camera scroll,
initialized background/palette and adult actor remain; the title is a second
high-priority actor, descriptor1CDEEC/pose290C62/palette3/origin0/0, not a third
background plane or a Simba roar animation. The prepared bitmap is256x48 at32/34;
transparent overlay crops centrally for256 width and can cover native scenery.
Source pixels match after the existing color expansion is normalized; that small
rounding difference is retained. No capability for other postfight/credits
backgrounds follows. [Ending scope and delivery evidence](ending-sunrise.md).
Older entries below are historical.

Public1554 adds a separately selected MD ending sunrise illustration. Its two
fixed64x32 planes, zero scroll, tiles, palette and one adult actor were verified
against actual ending initialization and six snapshots. See [ending sunrise](ending-sunrise.md).
No other ending/post-fight scene or background capability is inferred from this.
Existing installed policy31/scene-v3 packages remain unchanged. Older entries
below are history.

Current public build is **1434**, SpritePreparer1433 /sprite-v2 policy29.
[Bug Hunt coordinate and gameplay evidence](bug-hunt-gameplay.md).

The three MD Hunt collision maps contain an additional top row. After MD Y-16,
all8940 common floor-height cells and contact tags agree with the native worlds;
Hunt2/3 object-marker records also agree. Native rows97/26/41 correspond to MD
rows98/27/42. Raw row-aligned comparisons falsely suggested607/470/543 different
floor cells and led to an unpublished prototype; that floor overlay was removed.
1435 verifies the normalized data across every scene. Current code leaves the
shared floors/maps unchanged and imports only actual entry/marker differences.

Normalize each scene's coordinate origin before comparing collision/marker data.
This does not prove equal background layer counts, scrolling, initialization,
repetition or a complete renderer. Do not infer another scene's16px offset or
plane correspondence from this evidence. Existing scene-v3 /ScenePreparer787
and Hunt fixed-scene presentation are unchanged. Full MD bonus/game fidelity and
final original Genesis TAS remain incomplete; older entries below are history.

Current public build is **1198**, with SpritePreparer1182 / sprite-v2 policy15.
Launch `Play Available MD.cmd`. Existing settings and unrelated packages are
preserved; reapply F7 / Apply to enable newly available MD choices in an older
profile. [Bug Toss implementation and next work](bug-toss-gameplay.md).

MD Bug Toss now uses its original entry/arena width, complete320-pixel foreground
and world sprite origin, plus a native result/fade controller and prepared result
art/audio. Result flow, result artwork and result voice are independent choices.
Normal-stage entry random initialization is installed as prepared data.

**Full-game MD fidelity and the final installed Genesis TAS remain incomplete.**
The unchanged Genesis inputs return from Bug Toss at global input4200 with152
actual result reads, removing the previous23 extra reads. Next fix the concrete
level-two opening descent/landing divergence: sustained visible position gap
starts around global4230; the replay loses a life at global4537. Do not chase
isolated frame/pixel differences or alter the TAS. Use current5096 checkpoint
`build/fidelity1197-level2-route/second-start.state`, tape cut4200, rather than
replaying from boot. Current4100 save1185 and cut3756 remain suitable for bonus work.

Installed launcher1204/1205 also passes: the actual3x Windows card matches the
prepared renderer; no repeated live run was needed.

Component1202 qualifies focused model, original input route, actual Windows MD
and native256/SNES result captures, source-off control1190, native Setup1192,
data preservation1186 and result audio1193. Publication1203 selects1198 and runs
actual Setup. Helper data3,289,693 bytes;1466 images/981 bounds unchanged;
ScenePreparer787/scene-v3 unchanged. Player SHA256:
`5b6fa5887b7b363cb54b8661fd106ebf3b24593796eb7c8445b57a79f59b94c2`.

Background evidence1172b certifies Toss10 foreground/background and Hunt11-13
background only. Hunt12 foreground is1600x432 and Hunt13 is960x672 with scrolling;
do not treat their foregrounds as fixed320 pictures or as fully implemented.
Decoded assets alone are not renderer proof. The following entries are historical.

CURRENT1091: The missing MD interlevel scene is now identified independently.

Current public build is **1133**, with SpritePreparer1112 / sprite-v2 policy13.
The original MD animated interlevel illustration, voices, normal Start skip and
natural ending now run after the first hyena. Presence, graphics and sound are
independently selectable. Launch `Play Available MD.cmd`; existing settings and
all preceding images/bounds/gameplay data are preserved.
See [native interlevel scene and continuation evidence](pride-interlevel-native.md).

**The full MD-fidelity/TAS goal remains active and incomplete.** The unchanged
Genesis inputs now pass the illustration and Bug Toss into level two without
pausing. The12000-field route1137 still loses lives and stays in level two.
Next fix concrete Bug Toss rules/lifecycle: its native handoff consumes20 more
polls than MD. Do not alter the TAS to compensate. Use1117's4100 checkpoint and
cut3756, rather than replaying from boot. Ignore isolated pixel/frame differences
that an experienced player would not notice, per the user's latest instruction.

1134 source-off equality,1135 actual Setup,1136 real Windows illustration,
1138 preservation,1139 component qualification and1141 publication pass.
Sprite data3,184,746 bytes; all1466 images,981 bounds and prior six data sections
unchanged. ScenePreparer787/scene-v3 unchanged. Player SHA256:
`f67305ecc659194bb0c700ff29065ce63f92db3fcf6826b5629d67c23932ce6b`.
The following entries are historical.


Actual1104 initialization and two-plane/zero-scroll recipe1105/1106 are recorded
in [bonus/interlevel evidence](bonus-entry-interlevel.md). Those research
prototypes are OBSERVED, not a shipped renderer/capability or a TAS pass.

CURRENT989: Bonus10-13 fixed-background recipes are reviewed. Normal original
MD10/12/13 are captured;11 uses byte-identical source/initializer/update to12/13.
Initial stale line tables are classified as transitions. Foreground retains
native geometry/unmatched cells. Corresponding indexed jungle/wood colors fix
visible seams. ScenePreparer787/scene-v3 remains unchanged. See
[bonus evidence and limits](bonus-delivery.md). Post-fight07DB/ending and full
Stampede perspective retain native rendering. Earlier entries are historical.

CURRENT387: Public382 moves all8000 Pride contact cells and fixed Can't Wait
palette recipes into Setup's scene-v2 package. Installed playback loads those
tables; outdated explicit data requests Setup before play. Native gameplay,
independent sources and public372 artwork are retained. Default installation
and launchers upgraded, existing assets/settings retained. Read
docs/pride-prepared-contact.md (relative to project root).
Evidence: pride380 direct prepared-data/Setup checks, pride381 ordinary route
through victory/bonus to level1, pride383 real Windows boss view/error check,
pride384 scoped qualification, pride385 publication, pride386 helper links.
No cold polled replay claim:383's harness restarted its tape at poll0 after
loading3750. No save/game correction was justified. Full first-level goal OPEN.
Public382 SHA256:
c8393231f7e42a9afdbaabbb56b6e66c865a8bcf326f1a54b50a8968b6d0416e.

User priority: playable walkthrough and differences visible in ordinary play;
no instrument-only timing/one-frame transition refinements, no repeated
unrelated test matrices. Older notes below are historical and may be superseded.

CURRENT376: Public372 adds prepared MD foreground artwork in Can't Wait to
Be King (12391/12400 cells, nine native fallbacks), with independent palette
and scenery choices. Native collision/gameplay remain unchanged. Setup uses
the native scene preparer; default data and launchers are upgraded, settings
preserved. See docs/cant-wait-prepared-foreground.md (relative to project root).
Evidence: build/cant-wait373/report.json, cant-wait374-window/report.json and
cant-wait375-publication/report.json. Actual Windows view inspected. Full
first-level scope remains OPEN. Public372 SHA256:
6aab89332f2fc5b99373cb2de9a4804e61cd17ca1ca29ddc4e374bcd3b780537.
Earlier entries below describe historical releases and may be superseded.

User priority: check visible art, controls/combat and walkthrough progression.
Do not pursue instrument-only timing or one-frame transition differences.
Keep checks focused on affected code; no repeated unrelated test matrices.

# Background audit, 2026-11-05

2026-11-10 public362 adds [live Can't Wait Plane B](cant-wait-live-background.md).
Original initializer tables, one background plane with three horizontal scroll
regions and512-pixel source wrap come from the existing original recipe audit.
Native matching palette event drives MD colour steps; prior completed camera/
wrap inputs are retained, pause/repeated uploads hold. Native foreground and
sprites retain normal priority/windows/brightness/colour math. Native scenery
control, initial/moving/cold views and actual Windows client checked; real
ostrich-ride wrap1024 inspected. SceneReady(1) stays false; only background
availability is enabled. No other scene's layers or edge behavior are inferred.

2026-11-10 preview277 moves Pride caption images/palettes to installation data.
No image/layout/animation/height/scroll or gameplay-background recipe changes.
Five complete caption clients/guest scenes match268; actual installed Windows
centred caption inspected. Decoded images do not imply any additional scene
coverage. Other startup extraction paths remain migration work.

2026-11-10 preview268 centres the owned Pride caption at viewport width/2 for
native falling letters and MD picture, including camera clamps. Vertical offsets
and selected heights remain. Focused samples preserve guest state, actual Windows
client inspected. No background layer/scroll/initialization/edge recipe changes.

2026-11-10 preview260 publishes the independent Pride final-menu artwork choice.
Resumed246/247 verifies actual320 MD-timing menu clients against the same original-
verified sprite-only black-backdrop recipe. Native/MD widths/outcomes and both-way
source restarts pass; actual resumed world clients inspected. No gameplay layer,
scroll, initialization, edge mapping or renderer recipe changed in this follow-up.
260 corrects help text only; no new background capability follows.

2026-11-10 [menu source/viewport integration](pride-final-menu-source.md) corrects
HUD anchoring when256 centre pixels are transported into320.224 retains whole-
client failure; maintained226/228 corrected complete clients pass. Nine width,
five staged-source OS clients and UI toast inspected. Original sprite-only
menu/black backdrop/programs unchanged; no gameplay plane/scroll/edge recipe or
public capability changed. Source/lifecycle/release gates remain open.

2026-11-10 [native256 Continue artwork](pride-final-menu-native-continue.md)
extends private menu ownership to YES/NO and retained pre-consumption credits.
The original-verified MD sprite-only recipe/programs remain over black; actual
native loop/confirmation/brightness and exit-black retirement own duration.
Nine OS clients inspected, seven complete menu clients match verified pixels.
No gameplay-plane/scroll/edge correspondence, installer data, public capability
or maintained renderer changes.320/source/lifecycle integration remains open.

2026-11-10 [native-timing Game Over artwork](pride-final-menu-native-timing.md)
reuses the original-verified sprite-only MD menu over black. Read-only current
native/MD timeline observations establish initialization/ownership differences;
the new private bridge preserves native waits/brightness and retires before
later startup content despite a latched descriptor. Five OS images inspected
across controls/prototype, with complete prototype idle/fade pixel checks. No
gameplay plane/scroll/edge recipe or public graphics capability changed. Native
Continue and320 bridge contexts remain unqualified.

2026-11-09 [current background lifecycle](pride-background-lifecycle.md) checks
unchanged preview53 at three route positions/both widths/both Pride scenes.
Two paused MD/SNES/MD cycles restore exact OS clients; world strips change,
allother resources retained. Live/control14980 camera/latch trace rows and180
same-build resumed rows match exactly, with guest/media/scene checks. Lifecycle66
and history20 pass. No new layer/scroll/initialization/edge recipe, source
capability or renderer change follows; existing original scene evidence remains
the authority. No cross-build save compatibility was tested or required.

2026-11-09 [pickup flight movement](pride-pickup-flight-runtime.md) uses existing
ViewColumn to convert the pickup origin and replaces HUD stretching with a fixed
side offset for the two reviewed flights. Actual moving320 native/MD-art clients
and both camera paths were checked; guest/client/full PCM match execution modes.
No world-plane, scroll, initialization or edge recipe changes.

2026-11-09 [device queue priming](pride-audio-queue.md) changes only host audio
queue ownership around pause/turbo/load. Real paused/restored clients inspected;
six full routes preserve25 client/guest/full PCM. No scene layer/scroll/edge/
initialization recipe or graphics capability changes.

2026-11-09 [difficulty preservation](pride-restart-difficulty.md) changes ordinary
restart inputs. Actual256 completion/320 clients inspected. A wrong-width tape
failed with two deaths; the existing wide route then completes in both modes with
all8 lives and exact client/guest/PCM. No layer, scroll, edge or initialization
defect was established. No renderer/capability recipe changes in this phase.

2026-11-09 [independent title navigation](pride-title-navigation.md) adds a control
source, saved sampler and source-aware restart input helper. Actual menu/Options,
source tree and restarted Pride clients inspected; cub/scenery/audio independence
verified. No scene layer/scroll/initialization/edge recipe or complete MD title/
Options renderer follows from these control and lifecycle checks.

2026-11-09 [Options/navigation/new-game research](pride-title-options.md) records
actual clients and read-only native/original visible phases. Both versions have
the Simba interlude. Different phase boundaries provide no new per-scene layer,
scroll, initialization or edge mapping. No renderer or public source capability
is enabled; canonical first-visible timing is scoped to the measured profile.
The actual320 Options-return620 picture retains a native corner/window effect.
Do not infer a missing repeated backdrop or a completed return compositor from
that intermediate endpoint; any renderer change needs its own phase evidence.

2026-11-09 [maintained title readiness](pride-title-ready-runtime.md) changes title
controller timing and serialized input history. Actual menu/newgame/selected MD
arena clients inspected at256/320; supported cub/scenery/audio mixtures pass.
No layer/scroll/initialization/edge recipe or complete MD title renderer follows
from these results. Public/source capability reporting remains unchanged.

2026-11-09 [title readiness prototype](pride-title-readiness-prototype.md) verifies
input outcomes and native title actor retiming in research only. Actual title/
newgame clients at256/320 inspected. No layer/scroll/initialization/edge recipe
or independent MD title renderer follows; maintained capabilities unchanged.

2026-11-09 [compiled title upload](pride-title-upload-runtime.md) verifies actual
normal/LLE title timing, cold client/guest/PCM and supported MD audio/cub/scenery
mixtures. Title/selected arena/newgame windows inspected. Audio transfer changes
no background layer/scroll/initialization/edge recipe; source capabilities stay
unchanged and an independent complete MD title renderer is not claimed.

2026-11-09 [real-driver upload prototype](pride-title-upload-prototype.md) changes
research audio preparation time only. Actual Windows title/newgame/cold clients
inspected. No layer/scroll/initialization/edge mapping or independent title-art
capability follows from the faster audio transfer. Normal compiled support is
explicitly unimplemented and fails its retained probe.

2026-11-09 [startup sound bank preparation](pride-title-bank-preparation.md)
changes audio installer data only. Read-only current-player observer preserves
actual Windows client/guest/PCM in both widths. No new background layer/scroll/
initialization/edge mapping or renderer capability is inferred or enabled.

2026-11-09 [installed title-return data](pride-title-native-installed.md) verifies
ten native decoder payloads against actual original exits atbothwidths. Actual
Windows title/newgame/cold clients checked. This changes preparation duration,
not gameplay layer/scroll/initialization/edge mappings or title source support.
Decoded native title bytes are not proof of an independent MD title renderer.

2026-11-09 [title readiness research](pride-game-over-title-readiness.md) records
ten current native setup decoder intervals and the original MD Start boundary.
The neutral Windows observer preserves full client/guest/PCM at both widths.
Decoder endpoints alone are not proof of title layers/scroll/initialization or
mixed-title rendering. No new background mapping/capability is claimed.

2026-11-09 [Game Over exits](pride-game-over-exits.md) checks complete original
sprite-on-black menu pictures through input/timeout fade and black at256/320,
plus actual Windows later newgame. No gameplay layer/scroll/initialization/edge
recipe changes or new public renderer capabilities. Next-title timing remains
93fields late; do not infer that title or broader gameplay presentation matches.

2026-11-09 [menu right-edge placement](pride-final-menu-layout.md) corrects the
earlier visual clipping claim: all digit pixels already fit. Original SNES/MD
setup establishes common credit HUD edge distances, now preserved at256/320.
No gameplay plane, scroll, initialization or edge-repeat recipe changes. Full
Windows menu/fade/cold/gameplay clients checked; public capabilities unchanged.

2026-11-09 [confirmed MD menu drawing](pride-final-menu-yes.md) matches continuous
original sprite composition through YES hold/exit/fade using installed data.
No gameplay plane mapping, background scroll or edge-repeat rule is inferred.
The subsequent pixel audit disproved the reported clipping; see placement above. Full-width
Windows exit/fade and level handoff were inspected. Public capabilities unchanged.

2026-11-09 [installed MD menu drawing](pride-final-menu-drawing.md) uses prepared
sprite images, layout/banks and animation programs to reproduce sampled original
Continue/Game Over canvases over black. Actual Windows full/cropped views and
incoming MD palette steps are checked; NO retains that selected canvas through
fade/cold load. No gameplay-plane mapping or repeat/edge rule is added. Confirmed
YES/dismissal and native-timing source combinations remain incomplete; no new
public renderer capability is advertised.

2026-11-08 [installer-prepared menu assets](pride-final-art-package.md) identifies
the original compressed bank at ROM299A6E -> RAM0190,27872 bytes. Full banks match
the two original contexts at sampled97 onward;90/96 precede completion. Palette
ROM1D78AA matches original full CRAM. The separate installer decoder/package
reader reproduces the observed22 indexed images without reading captured RAM
at playback. No new scene renderer, layer mapping, timing or edge rule is claimed.

2026-11-08 [original final-menu artwork](pride-final-menu-art.md) establishes
scene-specific composition for20 initialized Continue/Game Over pictures.
Actual visible plane A/B samples are transparent; the linked sprite table,
submitted VRAM tiles and CRAM reconstruct every original pixel over black.
Initialization snapshots90/96/97/100 and later VDP/scroll/window state are retained.
RAM-aware ROM metadata accounts for all visible sampled sprite pieces; the
decoded graphics-bank ROM loader remains unproven. No gameplay-plane mapping,
edge/repeat recipe, complete animation coverage or production renderer is added.

2026-11-08 [selectable final-life transition](pride-final-resource.md) integrates
the established selected canvases and arena phase rules into the F12 resource
tree. Source commits during an owned fade use a real level restart; reset and
cold/UI loads retain their owned presentation lifecycle. Actual Windows clients
and full-route parity are checked. No scene layer/scroll/init/edge recipe or MD
menu renderer is added. Native menu artwork remains an explicit fallback.

2026-11-08 [width-aware final canvases](pride-final-wide.md) extends existing
selected origin/incoming capture to320 pixels, preserving its complete margins
across fades and saves. The established arena pending foreground/fixed backdrop
phase applies unchanged. Actual selected320 clients, cold continuations and
incoming whole-client phase projection are verified. This adds canvas ownership,
not a layer mapping, initialization, repeat/edge rule or MD menu renderer.

2026-11-08 [arena final-life presentation](pride-final-arena.md) records one final
foreground latch with a fixed MD backdrop. Original horizontal A/B words change
797/839РІвЂ вЂ™799/839, world camera stays1249/194, and vertical194/15 remains fixed.
The corrected private native256 capture lets foreground/native raster state
latch while holding the projected MD background phase. Actual native/scenery/
sprite clients and cold0РІвЂ вЂ™1 preserve their measured scroll and selected pixels.
TLKVIEW1 v3 retains the last map already verified against native VRAM, needed
while guest RAM is overwritten; map agreement still determines stage detection.
No layer count, source-plane correspondence, initialization or edge/repeat
recipe is added. No broader scene/rendering capability is inferred.

2026-11-08 [NO/timeout outgoing fade](pride-title-exit-fade.md) freezes an actual
initialized native menu canvas, including its real displayed Rafiki phase, and
applies a verified outgoing phase clock. New source timestamps preserve that
picture across saves. Real Window/source-pixel checks do not establish a new
decoder, layer mapping, scrolling/edge rule or MD menu renderer. Native title
initialization still supplies its own existing layers; no recipe/capability changes.

2026-11-08 [final-life saves/reset](pride-final-scene-saves.md) serializes the
four existing owned canvases with native/bank state. Cold and active loads,
reset and the next Game Over are checked in actual Windows clients. No layer,
scroll, initialization, edge or source correspondence is added. These cached
pictures remain scene-specific presentation state, not a background decoder or
evidence of a complete mixed renderer. Public capabilities are unchanged.

2026-11-08 [Continue transition](pride-continue-transition.md) privately recomposes
the existing initialized native Pride snapshot at full master brightness for
an independently timed incoming fade. It preserves all captured layer/scroll/
object/colour-math/source settings, rejects forced blank or any fallback line,
then restores the host snapshot/statistics. Actual408 scene/client and neutral
guest/window/PCM evidence are retained. No guest PPU state, new layer mapping,
edge/repeat rule, background decoder or MD capability changes. The native256
Continue UI mask is scene-specific and excluded; it is not generic layer proof.

2026-11-08 [excluded final scene prototype](pride-final-scene-prototype.md)
freezes the actual native last-hit canvas and fades it before the destination
scene. Actual256 Windows pixels are checked; no new background decoder, layer
mapping, scroll or edge rule is claimed. The owned black canvas covers stale
underlying native HUD during loading. Mixed-source masks and other scenes remain
unverified; the public background capabilities are unchanged.

2026-11-08 [final-life video evidence](pride-final-presentation.md) verifies
complete frozen-frame fades for original MD Continue and single-life Game Over
contexts. It establishes displayed picture behavior, not a new layer decoder,
scroll/initialization recipe, plane mapping or repeat rule. The current player's
separate native last-life path was captured through real Windows clients.
No renderer or background capability changed.

2026-11-08 [arena revival repair](pride-arena-revival.md) enables the selected MD
clock for nonfinal health death in the hyena arena. Actual arena recipes/planes
and full composed RGB are exported per capture, including both256/320 widths
and native/MD scenery choices. Native camera1316/198, MD background1316/199,
main19/sub0 are observed for this fatal entry. No scenery sampler, layer count,
plane mapping or edge policy changed. The original loader restores the main
scene's collected checkpoint. Do not infer later-level or final-life coverage.

2026-11-08 [fixed pickup flights](pride-pickup-flight-art.md) change only guarded
sprite art/palette ownership and placement. Actual256/320 client differences
stay within original native/MD pickup image bounds; native clients, completion
clients and guest/audio stay exact. No scene layer/scroll/initialization/edge
recipe changed and no additional MD background capability is earned.

2026-11-08 [standalone player](pride-standalone-player.md) retains all renderer/
game code, section sizes and relocations; the sole module-data difference is
a reviewed diagnostic build id. Actual new completion/boss/card/choice/title
Windows clients were inspected. No layer, scroll, initialization, edge recipe
or MD scene capability changed. Native card rendering and per-scene evidence
requirements remain intact.

2026-11-08 [maintained guest generation](pride-owned-guest.md) changes no scene
recipe, plane/layer mapping, scroll, initialization or edge policy. Newly
compiled guest/host/runtime objects retain full code/data/relocations, and real
completion/loaded-card Windows clients were inspected. The native card remains
native; no additional MD rendering capability is earned by rebuilding code.

2026-11-08 [fresh core/presenter build](pride-owned-core.md) moves the existing
hand-written presenter into owned source and recompiles it. Complete renderer
section bytes/sizes/relocations equal the preceding object. Actual new boss,
completion, loaded native-card and resumed next-level clients were inspected.
No recipe, layer/scroll/initialization/edge policy or rendered-scene capability
changed. Native card fallback and per-scene evidence requirements remain intact.

2026-11-08 [owned host migration](pride-owned-host.md) changes no background
recipe, layer count, scroll or edge policy. Actual boss, resource-choice and
resumed next-level Windows clients were inspected alongside exact whole-client/
guest/PCM replays. All host machine code/data/relocations remain identical.
No additional scene receives MD rendering capability; per-scene evidence and
native fallbacks remain required.

## Narrow-view completion/save continuation, 2026-11-08

The new256 completion and ordinary boss/native-card save tests change no
background recipe or renderer. Actual512x448 boss-slot, native black transition
and resumed next-level clients were inspected alongside full guest hashes/PCM.
The native C005AB card retains native rendering; accepting its complete idle
Pride cache for saves grants no MD card capability or later-level layer evidence.
See [pride-width-finish.md](pride-width-finish.md). Per-scene background evidence
and native fallbacks remain required.


2026-11-08 [narrow-view contact/save I/O audit](pride-width-contact.md) inspects
real512x448/640x448 clients at the same first-level contact boundary and actual
loaded-save/F1/F5 clients. Guest hashes match preceding source-selected renders;
the temporary-file fix changes no recipe, layer count, plane mapping, scroll/
initialization or edge policy. No additional rendered-scene capability is earned.

2026-11-07 [stable save identity](pride-save-identity.md) retains both cold
revivals and cross-editor loaded scenes' RGB/fonts/objects/ground/layer bitmap
and initialization/scroll evidence exactly:3142838278 artifact bytes across20
RGB artifacts. This changes no recipe/layer mapping/edge policy and adds no
rendered-level capability.

2026-11-07 [paged resource help](pride-tree-help.md) verifies484096 opaque modal
pixels in real native256/MD320 clients and retains guest/full PCM/native clients.
It changes no background recipe, layer count, scroll/initialization or edge
policy and adds no scene capability.

2026-11-07 [plain-SDL resource tree](pride-soft-tree.md) verifies centred menu
editing at both256/320 widths, resize and mouse mapping with actual OS captures.
It changes no background recipe, layer/scroll/initialization evidence or edge
policy and earns no additional rendered-scene capability.

2026-11-07 [one-pass frontend](pride-singlepass.md) paints overlays after selecting
the actual mixed canvas. Independent notification/turbo oracles retain1605632
complete client pixels; eight owned-reset cases retain both cold scenes' RGB,
masks, grounding and layer/scroll/initialization data. UI is kept out of wide
draw/save materialization. This changes no scenery recipe, layer count, plane
mapping or edge policy and establishes no additional rendered-level coverage.

2026-11-07 [reset integration](pride-reset-integration.md) retains complete cold
scene RGB/masks/fonts/grounding and layer/scroll/initialization records after
CLI-loaded practice and private owned machine resets. The latter exposed a
native startup RAM/audio discrepancy hidden by matching pictures: retained
alternating-field phase. The shared reset now clears it. All eight fixed private
reset cases retain both cold scenes exactly; native75/All Bugs and the strict
256-check aggregate pass. An actual OS game client after MD reset was captured
and inspected. No plane correspondence, new layer count, edge
policy or additional rendered-level coverage is inferred.

2026-11-07 [actual source restart](pride-source-lifecycle.md) retains the current
scene prefix when music/start choice aborts a revival, then reproduces cold
per-scene layer/scroll/initialization evidence, RGB/masks and grounding after
restart/F9.13113 native video/WRAM fields and complete PCM segments match normal/
cold controls. Actual ownedF1 files also preserve remaining scene data across CPU
modes with MD audio. No plane correspondence, edge-repeat policy or scene coverage
is inferred; final client comparisons exclude the intended elapsed-run value.

2026-11-07 [native raster continuation](pride-raster-state.md) proves a first-load
video discrepancy before mixed composition (286 native fields, identical WRAM).
Preserving actual completed/recording PPU register journals fixes the load rather
than hiding the differing age0 scene. Native and selected-MD-audio actual F9 runs
retain9253 native video/WRAM fields and exact aborted/replayed scene recipes,
RGB/masks/scroll/init records. This changes no plane correspondence, edge policy,
layer count or frozen-scene geometry. Native75/60648 All Bugs/early-state gates
now pass; eight first/eighth loaded windows retain1032192 complete client pixels,
including selected MD audio. Damaged-raster F5 rejection also retains the owned
scene. This remains private proof, not additional rendered-level coverage.

2026-11-07 [mixed notification composition](pride-overlay.md) fixes native PPU
background/HUD colors copied through translucent host panels. Panels now blend
against the actual completed mixed canvas in an excluded candidate. Five actual
Windows cases retain guest/native PCM and owned layer/scroll/initialization
records;1318912 client pixels match an independent mixed-pixel oracle. This adds
no plane correspondence, layer-count or edge-repeat assumption. Other overlays
and public integration remain open.

2026-11-07 [live menu/palette lifecycle](pride-live-lifecycle.md) retains the exact
owned scene recipe across repeated paused presentations, including native301
before HUD handoff. Cub-palette changes at101/275 match final-choice cold records
after transition, with existing layers/scroll/origin/init and priority masks.
82044928 scene pixels and1089536 complete clients pass. No other leaf, layer
count, edge repetition or general cross-scene source-change rule is established.

2026-11-07 [actual load-error UI](pride-live-error-ui.md) checks full notifications
against native PPU/font/panel/wide-overlay composition, while keeping the scene's
layer recipe and masks.99362816 owned scene pixels and1318912 client pixels pass.
Actual F10 changes cub palette only after completed release; no general source
change during frozen revival, layer count, scroll origin or edge-repeat claim.

2026-11-07 [live rejected-load audit](pride-reject-rollback.md) retains the exact
frozen scene history before/after rejected loads and exact subsequent composed
records in native256/full-MD320 defaults and native-start checkpoints. Eight
cases deliberately restore an earlier valid native state before injecting an
error, then verify restoration of the live state. No renderer/layer/scroll/init
code or edge policy changes; this is continuity evidence, not extra level coverage.

2026-11-07 [handoff save continuation](pride-handoff-state.md) preserves actual
default/checkpoint frozen layer, map, VRAM, scroll and initialization recipes
across processes.36 headless/12 Windows pairs retain170440704 remaining scene
pixels. The first loaded2331 native-HUD client matches uninterrupted presentation
in both CPU modes. Context-specific health/READY ages and actual OAM publication
are retained; no scene-independent layer count, origin, edge repeat or one-to-one
plane assumption is added. Same graphics profiles remain required on these loads.

2026-11-07 [normal actor publication](pride-normal-actor-handoff.md) retains
the existing frozen scene layer/scroll/initialization recipe. After a completed
normal OAM publication, ordinary actor composition provides source OBJ/BG priority,
windows and opaque-black coverage while prepared widgets finish their handoff.
No background offset or repetition rule compensates for the predecessor actor
failure. Diagnostic high-bit poses include the actor in the complete base;
compare final composed planes, not the changed intermediate representation.

2026-11-07 [selected starts and active handoff](pride-selected-start-revival.md)
retain the layer/scroll/initialization evidence. The new ready+2 actual-window
failure is confined to the actor region with identical guest state; the scene
still paints idle over a walking producer. Do not compensate with background
offsets, plane aliases, edge repetition, RGB transparency or longer handoff
deadlines. Native in-place and SDL edge HUD can occlude different actor pixels;
compare matching host options before comparing difference counts.

2026-11-07 [pre-fade grounding](pride-pre-fade-grounding.md) removes the default
revived actor's193->200 anchor jump by executing original floor contact before
the native draw. It changes neither layer/scroll evidence nor renderer offsets.
The26 Windows clients retain source OBJ/BG masks and per-scene origins; no
background-ready count, plane correspondence or edge-repeat assumption is added.

2026-11-07 default revival: [actor/priority evidence](pride-default-actor.md)
records source OBJ winners separately from BG priority. At the left edge of a
320-column view, an in-place native lives counter can cover the cub. SDL's edge
HUD option changes this placement; compare matching options before diagnosing a
layer or width error. Clipped native pieces can reuse a following visible
piece's OAM slot and do not own that slot. These scene-specific observations
add no general background-ready count, plane correspondence or edge repetition.

2026-11-07 checkpoint save continuation: the prepared renderer now preserves its
actual frozen per-line/VRAM/map/camera recipe across processes; see
[prepared state evidence](pride-prepared-state.md). This route's320-column MD
mixture has frozen origin36, not centered32. ViewColumn may choose any origin in
0..width-256 from camera/boundary evidence. This observation is scene/route bound;
it adds no general edge repetition or SNES/MD plane correspondence assumption.

The two versions must not share a fixed assumption about the number of background
layers. Hardware planes, apparent depth layers, scroll bands, and sprite effects
are different things. One plane can contain several independently scrolling bands;
one apparent background can also depend on palette animation or additional objects.

## Evidence collected

The native player now supports `--dump-scene PATH`. It records all 224 scanlines'
BG mode, main/sub enables, tilemap/character bases, four scroll pairs, windows and
colour-math settings. It also writes three raw SNES Mode 1 BG previews. These show
pixels before occlusion, windows and colour math; black includes transparent pixels.
Other modes retain register evidence but have no decoded preview. This diagnostic
does not change guest state or the mixed source choices.

`tools/audit_scenes.py` captured all fourteen SNES scenes, each paired with a mixed
presentation at the same frame. Every pair has identical guest frame/WRAM hashes.
Raw JSON, plane previews and final pictures are in `build/scene-audit/`.
The first contact sheets show the implementation **before** the background fallback
fix; they are retained as evidence of the Hakuna/Bug Toss defects.

All checked snapshots use Mode 1, with BG1 and BG2 enabled and BG3 disabled. This
is an observation at those frames, not proof of a two-layer limit for the entire
game. Stampede is Mode 1 at its sampled frame too, despite needing a special scene
adapter. Do not describe it as Mode 7 on the basis of its perspective appearance.

| ID | Scene | Sample frame | Distinct SNES BG2 scroll pairs | MD descriptor update | Static routine evidence |
|---|---|---|---|---|---|
| 0 | Pride Lands | 2300 | 1 | `08BA88` | Uniform camera X*38/256, Y*20/256 |
| 1 | Can't Wait to Be King | 2300 | 1 | `08BB28` | Horizontal bands; additional offset input |
| 2 | Elephant Graveyard | 2600 | 5 | `08BF34` | Band coefficient table `08C170` |
| 3 | Stampede | 2300 | 3 | `08BA88` | Descriptor shared with Pride; special scene path still required |
| 4 | Simba's Exile | 2300 | 5 | `08C26E` | Fixed section plus band coefficient table `08C17A` |
| 5 | Hakuna Matata | 2300 | 1 | `08DB82` | Half-speed X plus scroll-table writes |
| 6 | Simba's Destiny | 2300 | 5 | `08DFDA` | Multiple bands using `08C170` |
| 7 | Be Prepared | 2300 | 1 | `08E77C` | Half-speed X, fixed Y in this callback |
| 8 | Simba's Return | 2300 | 3 | `08E7E8` | Band coefficient table `08EA00` |
| 9 | Pride Rock | 2300 | 1 | `08E2B0` | Band coefficient table `08E532` |
| 10 | Bug Toss | 4500, replay | 1 | `08C252` | Fixed-scroll callback |
| 11 | Bug Hunt 1 | 2600 | 1 | `08C252` | Fixed-scroll callback |
| 12 | Bug Hunt 2 | 2600 | 1 | `08C252` | Fixed-scroll callback |
| 13 | Bug Hunt 3 | 2600 | 1 | `08C252` | Fixed-scroll callback |

These are scroll-pair counts, **not semantic layer counts**. Distinct positions
can arise from waves within one surface. Likewise, one scroll pair in a stationary
initial frame does not rule out multiple scrolling rates after the camera moves.
MD routine evidence comes from descriptor callback disassembly, not full live
captures of all MD stages. Initializers, other objects and interrupts can add work.

The initial Elephant Graveyard sample at frame 2300 had backgrounds temporarily
disabled; recapturing at 2600 avoided interpreting that as an empty scene. Bug
Toss level select had returned to Pride Lands by 2300, so its valid sample uses
the supplied All Bugs replay at 4500. Capture tools reject mismatched scene IDs
as evidence for the requested level instead of silently assigning their layers.

## MD plane check

`tools/md_plane_audit.py build/md-lab` inspects the standard native MD reference.
At the captured Pride Lands frame, both A and B contain graphics; the Window
registers are zero, with no visible Window region. A uses palette bank 2 and B
uses bank 1 in this snapshot. Sprites remain separate. The hardware map is 512x256,
while the decoded background source map is 512x360: source data must be streamed
into the hardware map. Its size is not a layer count.

The plane tool writes raw A/B previews and `planes.json`. It deliberately refuses
column V-scroll and interlace captures, which need different decoders. Previews
omit sprites, Window replacement, final priority and shadow/highlight composition.
Final-register snapshots alone cannot prove the absence of mid-frame changes.

The original MD all-bugs movie now provides a second, unforced Pride Lands
reference. `capture_md_reference.py` records it with matching BizHawk 2.11;
`md_replay_movie.py --lag-reference ... --background-audit` reproduces it in the
pinned research core using controller reads rather than video-frame inputs.
Across 2,913 visible original-game frames, every visible plane-B name-table cell,
the complete tile bank, uniform scroll mode and prior-camera parallax phase match.
There are 72 additional blank transition frames. The game clears/reuses tiles
before changing the old collision pointer, so pointer/level/player presence alone
does not establish visible scene ownership. Record display-enable and palette
state too. Do not interpret those offscreen clears as missing live background art.

`tools/md_pride_background.py` shares this checked recipe with the older forced
path diagnostic; that older diagnostic remains graphics evidence, never a
legitimate playthrough. Artifacts: `build/md-tas/bizhawk-verified/` and
`build/md-tas/replay-background/`. This adds full-level original background
coverage; it does not establish a different scene's recipe or full mixed-renderer
pixel equivalence.

## Defects found and current behavior

The earlier adapter treated each `+24` compressed background map as a complete
background, using the `+28` base tile blob and SNES scroll coordinates outside
Pride Lands. The contact sheets show this is insufficient: Hakuna Matata can show
tree/stripe patterns where distant mountains belong, and Bug Toss has wrong tile
patches. Scene initialization, tile-bank loading and scroll programs need separate
adapters. Successful decompression of twelve records did not validate twelve
complete backgrounds.

`TlkMdSceneReady` therefore means **decoded static assets**, while
`TlkMdSceneBackgroundReady` now permits **Pride Lands and Elephant Graveyard**. Other MD
background selections show `SNES fallback` in the tree and retain native SNES
background artwork. Foreground and scenery-palette selections stay independent;
choosing MD palettes can still recolour fallback artwork.

Pride Lands' expanded view also clamps its panorama origin to avoid negative
coordinates wrapping to the opposite end. Regression case: All Bugs frame 985,
camera (137,1055), native column 32, old background origin 20-32=-12. Do not apply
this clamp globally to other scenes; some will intentionally repeat or use raster
effects. MD layers bypass the SNES tilemap-ring mirror heuristic.

## Contract for the next scene adapters

Follow-up: `tools/audit_cant_wait_background.py` records a second-level timing
gap in an earlier unforced replay audit. The fresh execution trace now supersedes
those cached disagreement counters:8034 callback tables match the arithmetic,
and7944 visible VDP tables match the previous field's camera-plus-offset inputs.
Original RAM snapshots and four pictures are unchanged. The later
[wrap/palette audit](cant-wait-palette.md) checks both originals'512-pixel camera
wraps and39800 original MD palette-step writes. The descriptor palette is RAM;
checkpoint-only live selection fails. Native fade correspondence, dynamic scene
hydration, latched offset integration, mixed rendering and transitions remain.
Keep the native fallback; see [next-level artwork and audit](next-cub-art.md).

Represent a scene as a variable list of layers/effects, independent of console
plane indices. Each verified layer needs source provenance, maps and tile banks,
palette ownership/animation, priority rules, masks/blending, scrolling behavior,
and edge behavior. Preserve raster programs and sprite-based scenery where used.
Do not rename persistent resource IDs to hardware plane indices. The existing
Background node can select a whole verified scene recipe; finer child choices can
be introduced after semantic correspondence between versions is established.

For each next level:

1. Capture both originals at left/middle/right, top/bottom, and multiple times.
   Include camera motion, transitions, palette cycles, water/fire, and special modes.
2. Record live hardware state through scanlines. Isolate each plane and relevant
   sprites, then identify semantic layers and scroll bands. Record unknowns.
3. Trace the MD descriptor's **initializer and update**, extra graphics loads,
   palette writes, scroll tables and object-created effects. Port the complete recipe.
4. Compare source-native final pictures before testing cross-version combinations.
   Use the correct pixel aspect and matched world coordinates; a 256/320 crop is
   not a fair whole-screen comparison by itself.
5. Test layer count mismatches, transparency, sprite occlusion, tile priority,
   colour math, edges and live switching. Keep a native fallback for unsupported
   recipes. Require unchanged guest hashes for presentation-only adapters.

## SNES background with a wider viewport

The native Pride BG2 map is 64x32 cells (`BGSC=49`), with a 512-pixel horizontal
period. At All Bugs frame 1786 its horizontal scroll is 26. A centered 320-pixel
view adds 32 columns at the left, leaving six columns before source column zero.
Those columns previously wrapped to the far-right map and showed an unrelated
purple vertical strip. The Pride-only native background extension now repeats
source column zero there. Only added columns are clamped; the original 256
columns remain byte-identical. This is a live-map edge recipe, not a newly
decoded native panorama or a rule for other levels.

`tools/verify_pride_native_edges.py` captures actual 256/320-column SDL windows,
compares every original-view pixel, checks the six-column margin, and runs the
complete 5,000-frame native route with zero compositor mismatches. Evidence:
`build/pride-native-edges/report.json`. MD background handling remains separate.

## Reproduce

```powershell
powershell -ExecutionPolicy Bypass -File scripts/Build.ps1
python3.12.exe tools/audit_scenes.py
python3.12.exe tools/audit_scenes.py --levels 2 11 12 13 --frames 2600
python3.12.exe tools/audit_scenes.py --levels 10 --replay-frame 4500
python3.12.exe tools/audit_scenes.py --reuse
python3.12.exe tools/md_scroll_audit.py
python3.12.exe tools/md_plane_audit.py build/md-lab
```

The scroll disassembler needs Capstone in Python or `.tools/pythonlibs`; other
audit tools use the standard library. The MD plane command requires a prior
standard reference capture, built as described in [MD research](md-research.md).
Linear disassembly to the first RTS is a research aid, not a control-flow proof.

## Repeated revival freezes

The excluded repeated-revival candidate captures a new actual native background
publication per eligible death. The second scene's recipe, physical grounding,
camera/PPU history and draw records live in a separate scene-<entry-field> folder;
the first death's frozen pixels are never reused. Independent reconstruction of
both scenes across12 host/profile combinations verifies242966528 pixels. Sixteen
original-CPU grounding calls match full RAM/register results; real native/full-MD
Windows endpoint clients were inspected. See [repeated revival](pride-repeat.md).
  This does not infer equivalent planes, edge repetition or a recipe for other levels.

## First loaded field and source changes

The ordinary/practice candidate retains native view/camera history and the
complete cold initialization cache, without freezing an owned scene at save.
Its actual automatic startup saves resume with exact first/eighth SDL clients
in both widths (1032192 pixels), then freeze both later revival backgrounds
against actual new publications. Those full scene RGBs match prior proof;
an independent cub-frame change on ordinary load also passes. See
[practice saves](pride-practice.md). This does not equate console planes or
extend Pride's layer/edge recipe to other scenes. A separate notification bug
copies native background/HUD shading into mixed output; keep that UI issue open.

Moving-scene save1848 previously resumed1849 with raster camera443,352 but MD
background439,356 instead of continuous435,359; its sprite list was empty rather
than33 pieces. Save version3 fixes this by storing background history and both
latched/in-progress draw lists. The first loaded field now matches uninterrupted
window pixels, full scene records and guest hashes. Capture remains active with
a verified MD ROM even when displaying native media, preserving history for
subsequent source changes.

`verify_pride_presentation_state.py` passes eight moving cases at1700/1786/1848/
3000 (native and mixed saves each loaded with mixed media) and two paused cases
at1880. Pause comes from an ordinary Start controller input; the original guest
pause flag is checked separately through headless WRAM. Actual SDL window pixels
are compared, not inferred from the guest image. Three malformed history records
are rejected. Older v1/v2 saves contain no such history and use the legacy reset.


## Elephant Graveyard adapter, 2026-11-06

The original08BF34 callback and08C170 table give row lengths96/8/24/32/64 and
camera-X coefficients1/32,1/16,1/8,1/4,1/2. Vertical scroll remains0. Unforced
original video checks5,409 normal-palette visible frames: names, full base tile
bank and all224 line-scroll words match the preceding camera. Three literal VDP
captures yield215,040 cache-backed native pixel tokens with zero mismatches.
The source map is512x224 inside a512x256 hardware plane and repeats horizontally.
SNES band coefficients differ; no native-scroll substitution is used.

Actual Windows captures, source isolation, moving first-field save loads and
normal-controller completion through19400 all pass. Scene ownership is now
retained in presentation schema2; schema1 remains compatible for Pride.
See next-levels-status.md for commands, reports and unresolved second-level
palette/ostrich offsets. The source repertoire remains scene-specific.

## The Stampede and Exile delivery771

See [delivery evidence](stampede-exile-delivery.md). Exile initializer08C1C8,
update08C26E and table08C17A use a fixed152-line section followed by8/16/24/24
lines at1/16,1/8,1/4,1/2 X; Y=0. Four actual original captures have complete
matching base tiles/names; native C sampler749 matches286720 VDP pixel tokens.
Saved raster-camera history owns the phase; the MD background readiness now
includes actual Exile4. Foreground/colors remain separate.

Stampede retains native Mode1 perspective geometry, with original MD canyon
colors and an explicit matte-slot correspondence. H32 means256 columns. Its
generic decoded scene descriptor is not a complete MD perspective renderer;
background readiness still excludes3. This delivery does not equate semantic
planes across versions. Actual installed Windows clients775 verify both scenes.

## Hakuna/Destiny evidence783, before player integration

See [active progress](all-levels-progress.md). Hakuna requires an8192-byte raw
source map streamed into its64x32 hardware plane, four waterfall uploads and a
512-line scroll table windowed by5/16 camera Y. Destiny uses five fixed screen
bands with Y=0. New prepared-data C samplers match860160 tokens at12 actual MD
VDP states. Neither scene's player readiness is enabled yet; native ownership,
animation/camera history, prepared-payload eligibility and Windows mixed-scene
validation are next. Current Windows captures784 show native fallback only.

Private786 integration supersedes that pending status: saved raster history now
owns both scenes; saved six-update waterfall phase freezes at the original end
region. Helper787 prepares scene-v3 with full names/frames;788 imports it and
retains all860160 matching tokens, every other scene payload and common recipes.
789 independent selection/native picture/guest state/current save pass.790
traverses vertical and late Hakuna into healthy adult Destiny.791 real mixed
Windows captures at31030/34530/38030 pass. The bottom water bands also occur in
original MD video; do not remove authored bands as a presumed width/scroll bug.
Public849/860 and default Setup now publish scene-v3 with the actor/resource
delivery.861 verifies actual direct Hakuna/Destiny CMD clients. Public849 readiness7
remains false; private866 follows the independently verified recipe below.

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

## Return888-892 and public910

Return original initializer08EA06 installs line scroll8B03 and clears C60C.
Update08E7E8 uses coefficients08EA00={2000,4000,8000}:112/39/73 lines at
1/8,1/4,1/2 camera X, Y=0. Preserve39 lines, not40. Full map25899E,
tiles258C2A, all64 CRAM colors25D4F4 match five original49000..53000 VDP
captures.890 prepared-data C sampler matches358400 tokens.891 independent
source/native guest/picture/save checks and892 actual320-wide window pass.
Native8/descriptor0517 has its own BG1/BG2 history; no extra layer inferred.
Public910 now delivers both7/8 recipes plus owned actors/audio; scene-v3 data
was already complete for those backgrounds. Scene9 live palette differs from
static2698B4; its scenery and bonus scenery remain explicitly native.

## Pride Rock cave926-954, public949

Original initializer08E25E selects per-line scroll8B03, clears C60C and starts
its background actor. Update08E2B0 / coefficient table08E532={8000,4000,8000}
writes96/88/40 lines, Y=0. Full background2650D6, tiles265310 and four actual
VDP states match. Live CRAM is phase2 of08E538/08E5B8/08E638, not2698B4.
The original callback owns the three-step palette cycle; prepared TLKNXT04
stores it, a saved host scene clock advances it.932 imports scene-v3 and
matches286720 tokens;944 independent choices/native controls/current save pass.
Native descriptor0549 alone enables MD cave scenery. Summit07DB and ending
05AB/07A9 are separate scenes and deliberately retain native scenery/music.
934 real Scar/cave and940 victory windows inspected. Original921/924 timeouts
do not establish original summit/ending behavior. See pride-rock-delivery.md.


## Graveyard MD camera origin1786 / publication1791

The existing08BF34/08C170 five-band recipe (96/8/24/32/64 lines,
1/32,1/16,1/8,1/4,1/2 cameraX;Y0;512-wide horizontal repetition) is unchanged.
The existing Camera choice now enables the original shared08B7F2 MD camera for
scene2/C003EB with520x48 descriptor guard, verified original3840/544 limits and
128/210/64/20 vertical settings. Native raster cameraY=MDY-1 remains intentional.
Existing ViewColumn uses column0 for this genuine MD left-edge origin, rather
than a native256 crop centered in320. Existing MD streaming lead/row quantization
activate with the camera; no layer/plane reassignment or source-image change.
Five original moving/clamped camera samples agree, one differs1X and is left
alone.1790 binds source1785, actual full entry observation1788, and1789 source-off
full WRAM/picture plus selected saved AOT/LLE/actual Windows through15090. Actual
15055 client inspected. This supports camera origin/presentation only; later
Graveyard gameplay and the final full installed Genesis TAS remain incomplete.

2026-11-12: Exile camera/terrain1913

Original Exile camera ownership, initialization, targets, map limits and719
unforced samples are established by1901/1903/1918, plus original25000/25500
raw snapshots. The existing native Y+1 raster convention remains. Actual25525
Windows client was inspected. This changes camera tracking and collision
operands, with no new scenery decoder or layer claim: prior per-scene Exile749
layer/scroll/initialization evidence remains the renderer basis.681 sparse
terrain records are not proof of any background plane; sprite images and prior
scene/Stampede payloads are byte-preserved. Other normal-scene camera support
remains restricted until its own evidence is reviewed.


CURRENT3985: Public installed-preview3978 delivers original MD title opening
artwork and selected MD opening readiness. Player SHA
0e10a141591f9dfc0ac20a388751762b6a8a187bcb91507d1d2057f5734a95c3.
Actual Setup3984/Full Genesis CMD500 checked330 MD leaves. Preferences and ALL
prepared data except menu unchanged. Menu-v5 SHA
6ded071b41573dc0f39dc1439329832a21c236305e21c4b0e6c919073b8e5203;
clean CMake final helper3975 SHA
9feaa823f462dd2b3ad59d656565dc36f7f3e53f1e5237cb58eb08eb3bb6aeca.
Sprite helper3931/policy113/schema28/1524 images4471821 bytes retained;
sprite SHA8e1ee0841abee946071c078b97ab254f4aa3de779a5b746a47f31c62b663961e.
View9/audio5; all earlier monkey3954/Scar3932/Options3919 fixes retained.
All28/source goal ACTIVE. Final unchanged Genesis TAS NOT run yet.

Opening3963/3964: actual original title uses custom draw root90CA, next+2 and
direct position pointer+4; NOT generic128-byte gameplay actor slots/backlinks.
Logo290C62 at0,-16; Simba at0,32. Original two64x32 planes299414/2990EA,
tiles295864, palette2999EE, zero scroll. Separate logo, not baked into base.
Animation table28F3CE..28F446 is REVERSE order.14 observed frames29F252..29F5EA,
first field862; final977, selector/labels983. Extra29F652 table record never
submitted in opening/ready and is not shipped as an extra required pose.
Menu-v5 appends validated TLKTIO01-v2 opening data: two-plane backdrop,
14 Simba indexed records plus separate logo. Prior menu-v4 payload112: EXACT.
Setup alone decodes ROM; runtime only reads prepared data. No new animation
save clock. Existing main rootWord6E actionC462F6 phases3/9/4/5 supplies lifetime;
phase3 paints backdrop only, then logo/growth, final pose held. Recognize actual
C465F0 phase5 ready-controller construction, then existing row0/1 ready art.
Existing compiled C463FC seam/native C465C0 three-field UI constructor supplies
earlier MD readiness independently from graphics.menus.title. Existing
gameplay.menus.title_navigation owns behavior. Continue-specific transition
excluded. No generated C, framework, cursor/input-result or RNG edits.

3965/3969/3974/3977 archive changed maintained sources, registered in history.
3978 actual player/3975 actual CMake helper.3979 all14 IDs equal original draw
observations; five whole original VDP contexts861/880/900/930/960 match decoded
indices and actual C prepared-reader RGB.3980 five640-field source cases:
art changes preserve whole guest; both SNES choices match public3954 whole
guest AND window; four art/navigation combinations independent. Genuine430
checkpoint ->560 AOT/LLE whole guest and final window EXACT. No broad repeats.
3973 read-only clock observer exact to actual3968 guest/window establishes
logo424, ready548 vs original123-field interval: one field deliberately ignored.
3981 ACTUAL Windows growing460..468, roar516..524, ready550..558 all VIEWED;
final guest/window exact to dummy3980.3982 ordinary Down552/Start580 reaches
native OptionsC4690E row0 at620, window VIEWED.3984 actual public CMD500 title
opening image also VIEWED; installer produces exact qualified assets/binary.

Report1 remains PARTIAL: earlier publisher cards, audition/debug popup art,
returned-title contexts, title music/roar source coverage still open.
Important audio gap: tlk_audio.c scene_music explicitly excludes title;
audio.music.other has no supported title leaf. tlk_title_bank_prepare prepares
SNES native bank5, NOT MD title samples. New no-audio logs prove no audio claims.
Independent MD cursor/selection effects already present; do not call title
audio complete or silently disable native sounds without replacement evidence.

Remaining other reports/source gaps from CURRENT3962 still apply. User clarified
27 is Destiny's giant ONE-SHOT CHASING boulder, not normal rolling/falling rocks;
15 question mark is Stampede (already delivered3861). No further questions.
Next substantive work: title audio/source gaps OR actual remaining level
reports10,12,16,17,21,25,27 and partial coverage; monkey19-vs-native13 homes open.
Do not rerun working Hakuna grab fixtures3943/3944 or failed Destiny3939 route.
Do not mistake lava platforms3875/3876 for giant boulder. Final original TAS
only after remaining reports addressed. User process9328 untouched.



CURRENT4114: Public installed-preview4109 /340 MD leaves. Player SHA f95a5d922cc5e46f0cfb68d1cd0ea8b2431b443da89f8bc4d73aa3979a928be7.
Exile foreground now follows its full original MD map when BOTH MD foreground
artwork and gameplay.levels.simbas_exile.terrain are selected. Existing flags,
no new toggle, no gameplay/camera/audio/background-layer/scroll/animation or
prepared-asset changes. All prior herd color/coconut/monkey/gorilla/chase/bone/
menu fixes retained. Actual Setup and Full Genesis CMD4113 verifies same full
source tree as4090, preferences and ALL prepared assets byte-preserved.
Helper4084/policy116/schema28/1533 images4475824 bytes; final helper3975/menu-v5,
view9/audio5 unchanged. Full goal all28+source ACTIVE, final unchanged Genesis
TAS NOT run. User9328 untouched; no questions.

4107 independently decompresses BOTH original grids and validates exact
prepared map identity/dimensions: Exile100x155 cells /1600x2480 with same native
origin. Old cell-artwork correspondence retains native opacity:199 cells /
5690 opacity pixels differ from original MD map. Includes large filled/missing
floor regions nearbottom, not a sprite-offset or invisible timing issue.
4108 archives source/docs etc in history, adds Exile to EXISTING guarded full
foreground-map path used by Hakuna/Destiny. Same finite-map dimension guard;
native terrain or native foreground still selects prior remapped/native path.
4109 rebuilds only compositor on4096 graph, no frameworks/generated game edits.

4110 SEVEN224-field focused cases from genuine25500 through25724. Old research
state wrapperv4 histories rejected initially; extraction keeps36+guest-size
bytes and wrapperv2 ONLY, guest bytes unchanged. Do not implement old-save
compatibility for this. Current MD terrain art: same player975/2400 HP5/lives8,
camera796/2242 and entire guest/frame hashes as public4096. MD AOT/LLE guest/
window exact. Native terrain and native artwork INDEPENDENTLY restore old
whole guest/window (native terrain intentionally has different physics fromMD,
compare corresponding source controls, not cross-source whole state).
Current selected window changes7040 displayed pixels.4111 real complete old/new
packages, two250field local cases: identical guest/player/camera, same map
repair visible at lowercanyon floor/edge, images VIEWED. Old native remap fills
lower-right space incorrectly and loses original textured diagonal floor;
new full grid restores it.4112 qualifies;4113 publishes through Setup/launcher.
Future actual windows MUST use complete package, as learned4106 (bare executable
can show black Stampede world even for unchanged public binary).

Per-scene layer evidence unchanged: original Exile init08C1C8/update08C26E,
table08C17A fixed152lines then8/16/24/24 bands at1/16,1/8,1/4,1/2X,Y0; four
original VDP contexts and286720 tokens established749/771. This fix ONLY uses
the finite original foreground grid, no one-to-one plane assumption, repeating
edge inference or new background capability claim. Existing rasterY+1 retained.

Still NO exact reproduction of user screenshot5/6/10 hanging sprites; reports
16/17/25 remain open for that part, do not claim their hanging pictures fixed
from this broader map correction. Source-check candidate Exile runninglizard
7poses and chameleon5differences already have CURRENT map rows/roles and proper
Exile owner acceptance: C2CF90/B4F24 role3/bank7/MD0, C2F010/B80C4 role2/bank4/
MD3 etc. They are NOT established missing art merely because old731 exact-match
audit did not recognize shape/index variants. Don't blindly add duplicates or
offsets. No new enemy-art test/fix claimed. Other partial report coverage,
gorilla grab/shared victim sounds, menus/popups and final TAS still open.



CURRENT4123: Public installed-preview4118 /340 MD leaves. Player SHA d0e9373f93ec47de7f19fc01e7833dd2e59a92c20d646d1f5f8bc58bc6d27b13.
Three airborne ostrich poses now keep selected MD colors; existing independent
graphics.sprites.animals.ostriches.palette. No gameplay/timing/audio/artwork/
cache/format/resource-tree changes. Real Setup and Full Genesis CMD4122 verify
all previous choices/settings/prepared assets preserved. Helper4084/policy116/
schema28/1533 images4475824 bytes, final3975/menu-v5, view9/audio5 unchanged.
All previous Exile geometry4114/herd/coconut/monkey/gorilla/chase/menu/bone fixes
retained. Goal all28+remaining source ACTIVE, final unchanged Genesis TAS NOT run.
User9328 untouched; no questions. Previous turn is concrete progress.

4115 PRIVATE current wide-only observer: unique draws, all recognized palette
samples (instead of only pose disagreements), compact player rows. No guest
mutation; actual production equivalence for landing proved4119.4116 one2910f
genuine8000 second-ride continuation to10910 with exact original input cut7097,
same supported warm palette history3744 (do NOT discard this), no actor/RNG/
coordinate/tape edits. Ride naturally exits9678; no lost lives throughout,
final player5382/437 HP6/lives8.14 unique observed ostrich poses:11running plus
THREE unaccepted airborne poses C1D6B2/C1D725/C1D788, bank2/ownerC58C2C/action
C433B8. Existing678 recognized running samples all palette_matches1, but missing
air poses never reached that palette check: zero known-role errors was NOT
complete coverage. Existing metadata447 scanned ONLY3AD00..3B400, missing
airborne frames elsewhere. Don't repeat3000fields now: local8000 ride fixture
for85fields, and genuine10820 before-landing.state/exact2790-poll suffix retained.

4117 archives metadata/preparer/docs, extends whitelist12->15 known exact
shared poses (idle+11running+3airborne). All3 original indexed pixels AND anchors
EXACT direct ROM data: C1D6B2->MD0D082A (-45/-65,96x61), C1D725->0D0902
(-49/-65,99x48), C1D788->0D09AA (-45/-70,111x70). Corresponding native C26CB1 /
MD0B9070 streams each use20-field phases. Existing artwork-map rows already
correct: no replacement/new cache needed. Existing owner/bank/palette-hash
guards retained; original flashes not broadened. Canonical447 preparer updated
with explicit source pairs; historical447 report NOT rerun or overwritten.
4118 compositor-only build on4109 graph.4119 FIVE85f source-off/MD/AOT/LLE:
native source entire guest/window exact4109; selected AOT/LLE exact; pure color
fix preserves all guest/frame hashes. Third actual air pose changes5980pixels.
4120 actual COMPLETE old/new packages, all6 air images VIEWED: color flip fixed
in all3 large poses, full shared body/rider anchors unchanged. All other tests
not repeated.4121 qualifies,4122 publishes340 choices; no new switch invented.

HIPPO report7 successful landing is NOW checked on current production:
4116 correct final home5664, baseheight464, ten observed poses all mapped role24,
zero palette fallbacks. Simba at5678/473 enters landingC336B1 around10834, then
jumps C31484 from5674/473 around10836 and clears with HP6/lives8.4119 single
90f PUBLIC new-package continuation10820->10910 entire guest/window EXACT
optional observer reference.4120 actual contact/launch/clear3images VIEWED,
final guest/window exact dummy/current observer. Small mostly submerged teal
head is NORMAL: original MD1379/10710 and10750 images VIEWED, same underwater
head presentation. Do NOT invent a missing giant exposed body from those
captures. Previous source14 MD hippo drawings/anchors/palette1 verified3777,
independent art/palette/placement and final home shift retained3787/3788.
Reports6/7 now have concrete fixes plus normal encounter/landing evidence;
do not leave their old pending-successful-landing wording or keep rerunning it.
No new first-ride full-route/all-level/TAS/source-audio completion claim.

Still open: screenshot-specific Simba hangs16/17/25, remaining menus/publisher/
popups, other music-entry/transition contexts, Scar branches, hyena leap voice
variants, gorilla grab/shared victim audio and other actual source gaps. Final
unchanged Genesis TAS only after these are resolved. Native-only held-hang extra
death lead disproved4094; don't reopen. Exile enemy variants already mapped4114.


CURRENT4544 DELIVERY: Public installed-preview4537 /346 MD leaves/442 rows.
Launch Play Full Genesis.cmd. User supplied NEW slot1 field3529,paused1,
player2087/269,4HP/2lives, original copied4530 unchanged. It is NOT the earlier
8803 save4489. Two concrete ostrich reports FIXED in next four seconds:
- Giraffe disappears at initial ride start3593: MD foreground wrapped source
  by512 as soon as loop_base1888 initialized. Original MD4534 ride starts
  player2197/444, loop1888, wrap0: authored unwrapped map exactly matches all
 1148 PlaneA names/used tile bytes in three early states. Premature512 changes
 231/223/131 names. At first actual wrap512 original1189 names/tiles match
  wrapped source, unwrapped487 names wrong. Runtime waits for actual A58 wrap.
- Alive first warp3668 lost stage recognition because native streamed BG1 was
  compared with unwrapped RAM map; that reset MD palette100->0 and replayed
  its long fade. MapScore now uses the actual wrapped source below loop+viewport.
  Exact full user wrapper4542 old retained completed clock100->1; new retains100,
  same complete guest/native PPU; MD AOT/LLE exact. These are visible sustained
  defects, not tiny timing polishing. Native graphics source old/new exact.
23 previously omitted constructed ostrich head rasters have exact anchored /
indexed original4436 source matches and palette2 owner4443; current metadata
now admits38 total body/head poses and C58C38 under existing independent palette
choice and strict native-bank signature. No image/asset/helper/policy change;
private other policy123 candidate4509 remains undelivered. Finite King static /
ride planes, scrolling and dynamic source rules not generalized to other levels.

4538 current4519 graph ->4537 uses copied native payload for old identity, same
four-second Start/neutral gameplay, old/new whole guest/PPU exact, MD AOT/LLE.
4539 is research ONLY: old4493 identity graph plus same new compositor, allowing
full user wrapper history retained without migration/identity bypass in shipped
code.4542 full wrapper confirms source controls and palette100 retained atwarp.
Actual current-graph paced Windows4543 entry3594..3610 /postwrap3670..3686
VIEWED: giraffe visible atentry, correct steady orange scenery/pink ostrich
through loop; final guest/PPU/picture matches headless. Real Setup/Full Genesis
CMD4544 preserves all346 choices/settings/every asset/helper and prior1UP fix.
No broad all-ride-animation/all-source-coverage completion claim. Other reported
bugs, outgoing first-level SNES frames and final full original Genesis TAS OPEN.


CURRENT4808 DELIVERY: Public installed-preview4803; unchanged4789 player /356 MD leaves455 rows.
Installer now accepts original MD Graveyard decorative tiles using exact per-cell collision-height equality.206 previously rejected correspondences become original source art;12480/12480 complete authored foreground cell coverage. Original live Plane A1189 names/all used tiles exact; all other scenes, raster/map/palette arrays and gameplay payload unchanged. Focused80-field source/off/palette/AOT-LLE controls preserve guest/nativePPU/PCM, old291 foreground fallback records become0,568 displayed pixels corrected; actual old/new Windows VIEWED and endpoints exact. Player binary/source choices/audio/sprites unchanged. Other source contexts and all28-report goal remain open; final unchanged original Genesis TAS not run.

Scene helper4803 builds maintained md_assets codec with Graveyard per-cell floor
equality, as already supported for Pride/King. Old shape-only rejection kept
206 native decorative cells. All206 heights equal in both ROMs; two other
height differences retain opacity checks. Actual original657/entry VDP
1189 names/all used tiles exact4801. New cache4804 retains every other
scene, original raster/map/palette and gameplay byte. Graveyard paired coverage
12274->12480 of12480. Native map/live-word guards and unknown diagnostics retained.

Six80-field nearby source controls4805: original/native4 guest15000, no game
or RNG/pose writes. New MD291 foreground diagnostic records->0,568 display
pixels corrected; whole guest/nativePPU/fullPCM exact, native foreground
old/new exact, native palette independent, MD AOT/LLE exact. Actual old/new
Windows4806 VIEWED and each endpoint exact. Tests use identical native4
backends, isolated rendering proof, not full source-wrapper walkthrough.

Initial broad source inventory4797 from genuine old13600 retains native4 but
loses outer bonus-result origin; host exits126 at19262 with Missing initialized
bonus result origin. Not a new game defect or finalTAS failure. Do not rerun
that long extracted-backend continuation.4798 saved reusable full15000, with
original suffix cursor stored in run.log; command still references original
13600 guest/suffix. Nearby4805 md/after.state15080 is current-cache455 full
wrapper for local rendering; not proof of correct normal bonus history.

Real Setup/FullGenesis CMD4808 installs new scenes hash1c4459b26d33..., retains
all455 choices/settings/all other assets/helper binaries. Current player/audio
unchanged; private4404 still not shipped. No new toggle: existing foreground
and palettes selections control these original MD cells. No background scroll
or layer change; original five-band Graveyard recipe retained. Source audit
unknown sprites/audio and other28 reports remain open; Pumbaa natural life
catch/blink unverified. Final unchanged original Genesis TAS NOT RUN.


4867 scene cache change is marker-only Destiny hydration. All14 raster/map/
palette/floor/correspondence arrays and shared gameplay payload exact4860;
no new layer, scroll, initialization or renderer capability claim.

Ostrich review4896: no new layer/scroll/initialization recipe. Existing original
4534/4537 first-ride wrap initialization remains authoritative; current4892
nearby sequence and actual Windows4894 retain it. See qualified4895 scope;
local native4 continuation is not full-source/from-title background proof.

4906 debug popup: same original title Plane B/A maps and static scroll/initialization
recipe as Options/Sound Test, independently checked against actual VDP4897/4898
for six normal menu-control views. Low sprite labels precede high plane; sun
selector is high priority. Menu-v8 adds source-baked backdrop/labels and14 names
only; every previous plane/map/palette payload exact4901. Actual Windows4904
MD/native sources VIEWED. No gameplay-scene layer/scroll recipe changed.

4929 Sound Test separation: existing MD source two-plane recipe unchanged and
all old menu payload bytes retained4919. Native mixed style reuses captured
Mode1 BG1/BG2/OBJ/CG/window/math/scroll and changes only original BG3 text map
rectangle72..231/96..135; pre-override pixels equal untouched PPU exactly4925,
including native256 viewport. No world-scene layer/scroll/init changes. Native
song/font transfer is retained; actual settled mixed Windows4927 VIEWED.

CURRENT5058 natural initialization qualification, public5028 unchanged:
clean whole19120 session -> normal bonus result -> Stampede5047/5048.
Generic stage detection becomes0 during owned result19401; its controller
retains the origin canvas and supplies card art. Actual card19445..19458
VIEWED clean. Descriptor C0041D19592, music starts19593. Initial19635
capture is black initialization, not title-art proof. Actual19795..19806
Stampede VIEWED canyon/herd/player/HUD correctly composed; special canyon
is prepared/phase2 at21500 while generic BG-map stage remainsfalse. Do not
misreport capability from that generic flag or assume ordinary BG planes.

Natural Stampede->Exile5050 from full23900: outgoing frame and initialized
native guest retained; next descriptor C0044F24055. Early24055/24170
actual views black ordinary initialization; no active Exile proof there.
First generic stage1 captured24204 at raster33/183, MD camera33/183.
Endpoint24300 stage1/MD layout/caption/body buffer VIEWED; raster0/308,
MD previous-camera0/302, ordinary latched player149/508. Actual active
Exile later confirmed5054 at ordinary hangs192/545 and160/624. Native-grid
research reference changes only foreground topology, retains guest/PPU/
camera; current/legacy hands align in those contexts. No new background
scroll/layer change made, whole-level/every-transition closure not claimed.


CURRENT5883 visible Hunt/death handoff evidence (no new map/plane recipe):
Nearby genuine HuntII42877 has descriptorC00641, followed by native descriptor0
at42878..79 while its old raster remains visible. Retain outgoing level12 and
original descriptor table entry in presentation-only snapshot until nonzero
incoming descriptor. Preserve existing saved camera limits A6EC/D8 from
s_last_limits; otherwise StageMap overwrites the width with the cleared incoming
limit.5857 coherent320-wide canvas and5880 real window VIEWED. No guest RAM edit,
plane correspondence, repeating edges or guessed initialization added.

Death scenes use owned OBJ-only black canvas, not the previous world map.
Hakuna native health refills30468 before world raster30642: release on health
alone reveals a reflected native corpse/HUD. Retain selected MD death through
real world return. Stampede has separate hero taskC5858A and generic stagefalse;
its BG return is distinct from native health refill. King C3857F hazard splash
has finished before refill: retain finished black screen, no invented corpse.
Adult C37E76 non-stage health0 path shares the established MD body program.
Return53320 genuine native4 encounter has BGmode9 (Mode1), OBJ-only TM10/TS0,
no windows and retained CGADSUB19. Rejecting that retained color math exposed
native stock corpse/HUD despite selected MD death. Owned selected death canvas
now ignores native color math while retaining the exact line/window guards;
SNES death-motion choice retains original stock picture exactly5879. Actual
new Return53319 black and returned53498 world VIEWED5877. No new background
layer/scroll/init or source-asset claims. All ten natural death/return cycles
reviewed5881; not every hazard or final-life path.


CURRENT5944 game updates (no new background recipe): default native timing
shortens only RAM object projection/OAM assembly C0A531..A832, inside a pending
ordinary C3 player update before fresh draw upload. Descriptor/level/world-ready,
health, finish and hazard gates protect scene changes. Scripted programs,
Stampede, bonuses and death remain original. No map/layer/scroll/initialization,
edge-repeat assumptions, NMI/DMA/hardware-transfer or asset changes. Wide getters
expose live/latched fresh draw serials and captured-stage flag read-only; native256
observation does not select a wide viewport/spawn lead (guest/picture/PCM5940 exact).
Actual final paced Graveyard window5941 viewed with coherent bones/world/HUD and
separate UPDATES60.4/FPS60.4. Full unchanged route5934 reaches credits; ordinary
active completed-update minima56..60. Initial scene setup and scripted holds are
excluded; this audit adds performance evidence, not new background completeness.


CURRENT5971 Options/attract: original Options two-plane/static-scroll recipe is
unchanged. Bug was sprite-to-sprite overlap, not a new plane mapping: earlier
low-priority label sprites win against the high-priority Rafiki/logo sprite
before the winner is compared with planes. Previous grouped low/high sprite
oracle hid48 white label pixels that are visible in the actual original core.
Prepared Options now builds RAM glyphs before title decompression, draws title
sprites before the earlier SAT labels; font/palette/other menu payloads retained.
Three actual-core settings/cursor views match label/copyright white masks5968;
actual paced Options and title-return Windows5967 viewed. Exit root C465F0 keeps
old row/cursor for two fields; remaining startup countdown0 distinguishes real
opening phase5 from returned Options. Present coherent ready title, no native
flash/brief copyright disappearance; no guest PPU changes.
MD attract replaces controller data only; ordinary selected per-scene layer,
scroll, initialization and edge rules remain authoritative. Real Pride demo
window5969 viewed. No extra scenery capability, repeat rule or SNES/MD plane
correspondence assumed. Installed bone sprites retain existing original anchored
body/fragment art; sound source extension changes no geometry or background.


## Native scenery with Genesis ostrich camera:5992

Current5992 /installed-preview5987 fixes the visible ground-strip seam in both
ostrich rides with SNES scenery and the Genesis gameplay camera. The native BG1
ring exposes a stale strip after the ride warp; the compositor now samples the
original native foreground map across the full view using the existing per-ride
source addressing. Genesis foreground and SNES-camera pictures remain unchanged.
Focused first/second ride guest/nativePPU/shortPCM and original-timing AOT/LLE
controls pass5988/5989; real paced Windows5990 viewed. Publication5992 preserves
all495 choices, assets, helpers and settings. Gameplay/audio unchanged; no new
whole-game replay or claim that the broader source audit is complete.

Scene guard is the existing Cant Wait ride context (level1, descriptorC003B9,
active rideA56) and gameplay camera width320; SNES camera256 retains its VRAM
path, and MD foreground returns through its own earlier renderer. Native BG1
uses MapTile and the original native tile/palette data. Existing RideMapSourceX
retains entry until an actual camera warp, cumulative A58/512 strip addressing
and the distinct final-road row. No BG2 layer, scroll, initialization or edge
repeat rule was changed, and no correspondence between native/MD planes assumed.

Baseline5985 second ride8020 shows the gap in both the native PPU and presented
window; corrected5988/8020 is continuous while guest/nativePPU stay exact.
Entry/giraffe7918 remains exact. Six second-ride endpoints and two first-ride
endpoints checked; nearby controls5989 preserve selected MD foreground and SNES
camera pictures. Actual paced first/second windows5990 reviewed. The intentional
compositor repair can differ from the stale native PPU strip; PPU equality alone
does not qualify the mixed presentation. No whole-level or new full TAS claim.


## Native materials on Genesis terrain:6009

Destiny6 and Simba's Return8 with Genesis layout and SNES foreground have matching
map dimensions/origins but different authored shelves. At Destiny monkey2080,339
the selected MD shelf is near y336; at Return hyena1328,387 it is near y384. Native
map art leaves these real collision ledges absent, making grounded actors appear
misplaced. Baseline5994 and MD-ground/source controls5995 demonstrate the cause.

TlkMdSceneNativeLayoutTile reads the selected MD map and applies original native
8x8 indexed tiles/palettes. Exact indexed matches win; version-specific details
use closest native material with strong transparent-silhouette weighting. MD map
priority/flips are retained. This is an adaptation, not proof every tile has an
exact native counterpart. No MD bitmap substitution in SNES artwork mode. The
guard requires these validated scenes and matching map dimensions; diagnostic
foreground_geometry is md_layout_native_materials. Actor/collision data unchanged.

No BG2, scroll, initialization, edge-repeat recipe or plane correspondence changed.
FullMD/native-terrain picture controls and mixed guest/nativePPU pass6007. Final
diagnostic refinement and pictures requalified6008. Actual paced Windows6006 at
40700/40755 and50880/50935 show the missing shelves restored, later captures near
60 updates. These are focused nearby captures, not full-level renderer coverage.
Original ostrich seam5992 handling remains present. Publication6009 retains all
assets/policies and saves; decoded tile availability is not whole-renderer proof.

## Independent browser examples:6022

The new browser no longer uses the live game as its sprite comparison canvas.
Original normally loaded native graphics banks and prepared MD images provide
subject examples; four raster/palette combinations preserve independent choices.
Shared animals use the already reviewed indexed-raster identities. This is
preview infrastructure, not proof of every pose/scene's live ownership.

Scenery examples use the existing compositor in an isolated chosen level. No
layer, scroll, initialization, plane correspondence or edge-repeat recipe was
changed. The prior per-scene audits, mixed ledges6008 and ride seams5992 remain
the renderer evidence. Preview alpha/output validation is not renderer coverage.
Current UI gameplay illustrations are schematic, not exact affected-location
recordings. Source capability flags and the broader source audit remain intact.


## Vertical free-view evidence6175

The PPU/raster snapshot remains256x224. The separate host view can grow in both
axes at fixed pixel zoom, bounded256..1024 columns /128..768 rows. The original
camera and enemy activation are retained in Original gameplay mode. This does
not promise activation/drawing of actors the game has not submitted.

Each recognized normal scene still uses its existing independent artwork and
terrain sources. Extra foreground rows use `Bg1Origin` and the bounded live
level map/block lookup, or the existing reviewed MD foreground/mixed-material
sampler. Camera Y uses the original latched logical origin. The view stops at
map boundaries. No SNES/MD plane correspondence is newly assumed.

| Scene | Recognized world descriptor | Existing background evidence retained | Additional vertical area |
|---|---|---|---|
| Pride Lands | C00387 / C0080D | MD08BA88 finite panorama; X38/256,Y20/256; native captured BG state | Full world foreground; selected dominant boundary color outside224 |
| King | C003B9, ordinary terrain | Original MD per-line background recipe; native raster; separate ride-strip rules | Full foreground; boundary-color BG. Ostrich loop contexts keep224 |
| Graveyard | C003EB | MD08BF34/08C170 screen bands96/8/24/32/64; fixed BG Y | Full foreground and submitted bones/actors; boundary-color BG |
| Exile | C0044F | MD08C1C8/08C26E fixed first152 rows then8/16/24/24 | Full foreground; boundary-color BG |
| Hakuna | C00481 | MD08DB82 larger512-line table, Y5/16 and authored bands; native captured waterfall/raster state | Foreground extends; this delivery does not reconstruct the larger BG outside the selected original window |
| Destiny | C004B3 | MD08DFDA five bands96/16/32/48/32,Y0 | Full foreground; boundary-color BG; face-script context keeps224 |
| Be Prepared | C004E5 | MD08E77C/08E7A4 half camera X,Y0, preceding line DMA disabled | Full foreground; boundary-color BG |
| Simba's Return | C00517 | MD08E7E8/08EA00 bands112/39/73,Y0 | Existing MD geometry/native-material mapping extends; boundary-color BG |
| Pride Rock | C00549 ordinary world | MD08E2B0/08E532 bands96/88/40,Y0 | Full foreground; boundary-color BG. Summit/postfight use original framing |

The additional scanlines use the closest captured boundary's palette/priority
state. BG3 text is not tiled beyond its canvas. Beyond the captured background
window, the most frequent selected BG2 token in that boundary row supplies a
flat color; dithering/stars are not stretched into vertical stripes. This is a
conservative presentation extension, not proof of complete vertical parallax,
new background artwork or every unsampled dynamic scene. Selected MD colors do
not silently switch to SNES artwork. `view_area` reports width, height, original
row placement, scene capability and `dominant_edge_color` explicitly.

6153 samples each of the9 scenes in FullMD and native-art/MD-gameplay presets.
6160 preserves all18 guest hashes and all sampled world pixels through the
reuse optimization; its sole intended picture correction is native health HUD
edge placement. Initial direct-entry Graveyard6148 dies and is not terrain
acceptance; genuine nearby bone context5951 replaces it in6153/6160.6154 legacy
fixed16:9 controls preserve full guest/native/window hashes across all9 scenes.
6166 representative final guard path exact;6167 Stampede and ostrich retain
original framing and pictures. Final6173 actual paced windows inspected after
960x672?960x960 resize.6172 nearby death/return preserves guest, matches original
death picture, and resumes320 rows. No new full walkthrough/death-every-level
claim; the broader all28/source acceptance remains open.

## Console-framed ostrich rides6191

Scene evidence remains King C003B9 with the actual ride flag A56, covering
both existing ride strips.6184 actual1024-column windows expose the unsupported
strip extension and mixed-art rendering near30 updates/sec.6191 selects the
console viewport (320x224 for FullGenesis and SNES-artwork/Genesis-gameplay)
inside the same wide window. It does not synthesize another strip, assume
planes correspond, or alter the existing5992 native seam sampler, MD scenery
source/wrap, BG2 bands, scroll or palette initialization.

The latched ride flag gates host framing. The live same-scene flag constrains
camera width and spawn/parser margins within the CPU update, so entering a
ride cannot consume the preceding normal section's wide margin. Existing
canonical-view math stays intact.6189 verifies both rides in Original and
Extended camera controls: camera320 throughout, same whole guest/PPU at the
nearby endpoints.6187 actual post-fix windows and focused pacing compared to
6184 retain the genuine7980 backend/neutral holds. Mixed-art median33.187ms
becomes16.634ms; selected MD artwork18.447ms becomes16.670ms. Baseline optional
8100 save failed after capture/hash and is not accepted as a save test.

6188 runs unchanged original-controller input from title through all ten main
levels/credits for both presets at2048x448, with1024x224 normal-world rendering.
Original camera/enemies, no guest/actor/HP/RNG edits. All reference checkpoints
retain guest/PPU hashes; final10HP/8spares. Normal-world, both ride and credits
Windows captures inspected. Initial level-entry captures can coincide with
fades and are not positive terrain evidence; later world captures supplement
them. Source/renderer artwork choices remain independent. No full Extended-
camera, every-pixel, all-bonus/all-death, new save or complete vertical-
background reconstruction claim. Prior dominant-boundary-color height limit
remains accurately reported.

## Tall user-window evidence6199

The actual report uses SNES artwork and Genesis gameplay,2560x1511 at zoom3,
852x503 world view with Extended activation. Prior6188 completion was1024x224;
it did not exercise these added vertical bands.

Pride native BG1 remains the original scrolling world-map terrain. Native BG2
is the audited finite64x32-tile512x256 panorama with its existing uniform
scroll/raster initialization. Do not infer correspondence with either MD
plane. Keep the original224-row rendered panorama band at the bottom of the
expanded view, using each source row's own VRAM/CGRAM; above it use the dominant
native top-row sky token. This intentionally lays out a finite backdrop in a
larger canvas; it neither invents more mountains nor vertically repeats a
boundary column. The previous dominant bottom-color fill produced large green
bands. Scene metadata reports native_pride_bottom_anchored_band here only.
King and all other background policies still report dominant_edge_color;
no new layer mapping/parallax reconstruction or arbitrary edge-repeat claim.

Actor evidence is independent of decoded background availability. King giraffe
bodies are scenery; heads are separate C58D60/C58D70/C58D80 actors, poses
C07D93..C07F59. Their initial scan previously used380 columns while the actual
world displayed852. The host now supplies requested dimensions before raster
readiness, and the vertical queue/cull/draw rectangle includes the503-row view.
Submitted off-native head pieces can precede native graphics/palette DMA;
SNES frame selection therefore reads their bounded original pose planar source
and exact live animal palette when the private OBJ5 palette is stale. Selected
MD frame/palette adapters keep their existing source guards. All five nearby
heads appear in6197 actual King capture. This is not proof of every off-native
actor's staging behavior.

Evidence: build/fidelity6197-large-view-acceptance/report.json and actual-window
PNGs for Pride/King; initial King spawn trace1026 now852/298; original Pride
320x224 guest/PPU/window exact; King AOT/LLE oracle pair exact with render
acceleration disabled. The smooth-updates oracle experiment differed and was
not counted as a pass. A broadened animal-palette fingerprint experiment made
heads blue and was rejected; final PE sections equal the tested working build.
6201 final ride controls preserve320x224 and prior guest/PPU at the large window.
Other scene layer/scroll/initialization evidence above remains applicable.

## Four-report background and ride evidence6216

Normal King native BG2 metadata6218: BGSC0x49, mode9,224 rows all scroll0/0.
Pride6217/6203: same64x32 map shape, uniform per-frame sampled rows, own live
scroll75/131 or140/24. Original scene-specific initialization remains active.
These two native finite panoramas use the same bottom224-row presentation
band in taller views, their own source-row VRAM/CGRAM and top sky extension.
This deliberately extends a finite canvas and does not imply extra authored
art or identical original parallax. MD and other levels retain their own
existing recipes/capability limits.

Ostrich camera/script remain console width; presentation is independent. The
known running ring is512 world pixels. Existing original5458/5459 map/joint
initialization evidence remains relevant; only added presentation columns
normalize into that authored loop after wrapping. Native foreground now uses
its complete scene map in the ride, including available rows above the native
viewport, instead of clipping tree tops at224. Past the map, foreground stops
and sky continues. The native BG2 has64 columns; MD background sampling207 in
tlk_md_assets.c explicitly masks wx&511 after its per-line scroll calculation.
This proves per-row512-token periodicity for these selected King backgrounds,
not for other scenes. Foreground token reuse is gated on the wrapped ring.
Sprites, windows, colors and HUD compose separately and do not repeat.

Actual6210 both rides/both artwork presets,6213 four view shapes,6214 live-resize
natural traversal and6221 final maximum-view image were inspected. A prototype
clipping all foreground above the old ride viewport chopped branches and was
rejected; final samples the real map there. A sparse-sky cache comparison found
uninitialized background-token use near the right meter; the final guard skips
that cache on flat sky/partial views. Final maximum guest/PPU/world pixels
retained; only the corrected top-right HUD background differs from that trial.
No all-actor-prefetch, full vertical plane reconstruction or locked60fps claim.

Mufasa6212: selected controller had no prepared native illustration path and
previously painted black. The available Genesis illustration now displays with
SNES artwork presets too. UI/provenance state that native artwork is currently
unavailable. This is a declared source limitation, not proof that a decoded
native counterpart has been implemented. No assets/helpers changed.

## Stable tall presentation and bonus canvas6239

Native Pride/normal King keep the per-scene BG2 map/scroll/init evidence above.
The added top band now samples the authored panorama row0 with hofs0/vofs1023,
not the current camera-clipped screen row0. The token retains live palette and
color math. Other dominant edge tokens use12 completed updates of hysteresis;
this suppresses boundary flapping, not real fades. Tall presentation dead zone
is independent of the console camera and is saved in TLKVIEW1 v11.6229 jump
trace and actual Windows image show stable origin/sky while native y varies.
No new layers, infinite edge-repeat assumption or cross-console plane matching.

Bug Toss: native background/foreground use the existing static zero-scroll
256-pixel canvas. Genesis arena is320 wide. Fit each selected native plane to
the finite active arena width; retain selected MD planes' existing original320
recipe, clipping and sprite dimensions. The stage is fixed224 high.6235 actual
near-right Timon capture has artwork behind his full movement area;6226 native
WRAM/PPU exact at1800. This is explicitly a presentation adaptation.

Ride: original native foreground VRAM is authoritative within x0..255/y0..223,
including streamed hazard cells. Beyond it use the previously evidenced
512-pixel source ring and available authored map height. Do not repeat live
native hazard cells in the added512-column cache cycle. Native source pose
readers for off-native animal pieces retain bank7E/7F and use captured WRAM;
MD selected drawings remain on their prepared adapter. The ride presentation
origin stays fixed within each A56 loop key while the original camera jumps.
6233 actual live-resize captures and unchanged nearby controller route qualify
both ride exits,6HP/8spares. Wider script-prefetch trial failed encounter timing
and is excluded; full Extended TAS and all-obstacle-prefetch are unqualified.

## Complete native panoramas and raster-camera alignment6248

The earlier512x256 finite-image interpretation was incomplete: that is the
VRAM streaming ring, not the complete original BG2 name map. Descriptor+1A
Pride C9F9E1 decompresses to5760 bytes (64x45 names,512x360 pixels); King
EEE636 to3968 bytes (64x31 names,512x248). Original descriptor+06 tile data and
+0C palette independently render both maps. Source audit6246 matches every
57344 native BG2 pixel in each6244 sample with original per-line scroll,
including Pride source rows132..355. This explains why the prior camera slice
omitted the upper132 rows near the bottom of the level. Initial full-ring
trial6242 produced stale green/black rows and is not qualified.

Final preparation decodes the two bounded full maps once, with required byte
counts; tall composition uses their authored names and current original live
tile pixels, palette and priority. All source rows fit vertically to the tall
window; nearest-row sampling is a deliberate background presentation policy.
Horizontal Pride clamp/King wrap and original horizontal scroll remain distinct.
No sprite/terrain scale change, no new layer or scene-plane equivalence claim.
Selected MD backgrounds and other levels retain their existing evidence.

The tall field's translation now uses the completed raster camera already
derived by BackgroundFrame/Bg1Origin. Gameplay RAM can run ahead by-4..+7 pixels
in the nearby jump trace; using it caused residual whole-world vertical offsets
even with a stable tall origin.6244 Windows Pride/King images reviewed;6245
tall guest/PPU and fixed-canvas guest/PPU/window controls exact. No fresh full
walkthrough/TAS or all-scene performance assertion.

## Native tall panorama performance and King black bands6299

Authored Pride512x360/King512x248 maps and original initialization/scroll evidence
remain6246/6248. Cache original native BG2 tile tokens per live VRAM version,
validate tile data once per draw, and keep palette/brightness resolution live.
Native BG1 tile runs retain dictionary, flips, priority, palettes and canonical
VRAM behavior.6257 normal-window and6263 maximum-window controls are pixel exact
to the preceding slow renderer, with identical complete guest/PPU hashes.

Added horizontal native BG2 area now uses periodic mirrored image copies,
including after multiple periods/scrolling. This is a deliberate presentation
extension requested by the user, not evidence of infinite authored scenery or
a generic plane-equivalence rule. Selected MD backgrounds keep their paths.

User video37.7..38sec reproduces at King4043: native raster has12 forced-blank
lines, INIDISP128 at top, which tall extension expanded into a huge black band.
Use nearest valid completed stage line for tall first-two-level metadata and
panorama palette-row selection; preserve entirely-dark rasters/real fades.
6296 final old/new same-start complete WRAM/PPU exact.6297 actual Windows held-
frame captures show the black band removed; only diagnostic presenter delays
were used for external capture, and those are not shipped. Earlier6296 cold
one-field shutdown captures were black on both builds and are inconclusive.
Ride preview/map rewrite prototype is excluded; original ride policy remains.

## Ostrich road and finite script presentation6335

Scene C003B9 native foreground map is6400x496; original per-scene ride source
rules retain the first/second loop bases and last16-pixel road-row initialization.
Use one map source across native and extra columns, not a live256-column VRAM
patch beside static added columns. Extra right columns repeat the evidenced
512 road strip even before actual camera wrap. Native mirror heuristics are
disabled for this scene. Tall/short views anchor map bottom to window bottom.
Separate native BG2 remains the verified512x248 panorama, with live tiles,
palette, scroll and its existing full-height fit. Selected MD scenery retains
its own recipe; no general full-height MD background reconstruction claim.

Future obstacle art comes from the original finite event records and the five
poses/constructors audited4686 (ground plus two branch/collider families).
Decode static WRAM art, project with original event distance/spawn offset,
select independent native/MD frame/palette, and retire the preview when actual
actors take ownership. MD frames use complete prepared MD bounds/default bank
sampler, not the restricted explicit-bank alias sampler. Actual actor drawing
bounds span the picture while original script/contact timing remains authoritative.

6327 real entry and6323 real live-resize images reviewed: continuous road,
visible future obstacles, both exits/landings to next checkpoint6HP/8spares.
6330/6332 final native/MD preview samples visible. Original maps/script evidence
is specific to these two King rides; no scene-plane equivalence/infinite-world
assumption.6322 tile-run optimization preserves guest/PPU/world pixels; small
HUD border-background differences are disclosed rather than called exact.

## Follow-up finite ride/panorama evidence6365

Slot1 actual18309 native BG2 hofs508 crosses its512-wide hardware scroll wrap;
the extra mirrored image pair is1024 wide. Unwrap completed native phase before
sampling that pair; retain source tiles, live palette and original scroll delta.
Store presentation phase/level in history12. This changes the added-area mirror
policy, not original scenery/world geometry or inferred plane correspondence.

King's initialized6400x496 map and source layer registers remain valid while
its new running strip names stream (user9363..). Preserve tall presentation
through that specific transition, not arbitrary map disagreement in other scenes.

Finite event terminal distance supplies remaining512-wrap count. Project the
authored exit terrain and flat head, not an infinite road, into added forward
columns; the repeated-row token cache stops at that boundary. Two actual flat
head markers2768/288,4288/288 equal loop + selected viewport +560. Read-only
C07F59/native ROM art or prepared MD counterpart, with independent giraffe
frames/palette, supplies its head until actual submission. Old mounting heads
are not drawn over the running ring after travel512. Original terminal scan
owns births; no early-spawn experiment ships. Sprite origin and head/body
priority follow original submission.6362 both rides/landings + actual resized
Windows viewed;6354 actual complete native exit and6361 selected-MD exit viewed.
Final6367 loop-invariant hoist preserves whole guest/PPU/window while reducing
cost. No all-scene, full MD background-height or full-game equivalence claim.


## Destiny high-resolution initialization and material rows:6414

Current6414 /installed-preview6410 fixes the reproduced Destiny high-resolution
startup lockup. Same Play SNES Visuals with Genesis Gameplay.cmd; all501 choices,
installed assets/helpers/user INIs and prior ride/pickup/Timon fixes retained.
Binary262e4e64738828271f121bffa61a0688efe427da6e1737911297b96476014b03.
Only pride_final_wide.obj and tlk_camera.obj change against6393.

Saved user slot4 host93264 already has age0/action0 and no Simba/main HUD;
normal-size loading is also stuck. Do not repair its guest/header/source state.
Restart Destiny through level select after reopening the launcher. Fresh original
entry at2560x1511/852x503 reproduced the same failure with expanded streaming;
320x224 and large/no-expansion controls initialize adult normally. Original
loader scans/camera flight now retain original bounds until the live source
player C5858A/C3 controller exists; normal expanded streaming then resumes.
Bonus controller paths and their bounds are unchanged.

Wider camera max can shrink by532 pixels at the live handoff. Instant clamp
left the native tile ring stale and stage detection false indefinitely. Approach
the new max in original eight-pixel steps, retaining each original streaming
update. No backdrop/plane/scroll recipe changed. Native MD-layout material rows
reuse existing tile-run decoding and native palette caches under no-sprite,
no-window/no-BG3/no-layer-math eight-pixel-layer guards. Scalar versus optimized
movement endpoints preserve whole guest/nativePPU/window exactly. Measured
120-field moving scene49.280ms median/p9558.960 becomes21.593/p9525.605; this is
still below60fps at this large view, not a universal performance guarantee.

6411 final fresh mixed and FullMD Destiny and related Pride entry all show full
852x503 stage. Ordinary left/jump input moves4738->4443,4HP/2spares;99/99 fresh
updates in the measured active range. Actual DPI-aware paced Windows capture
reviewed. OriginalTiming compiled/LLE30-field same-input guest/native/window
exact. Related Return6412a five-field scalar/row control also whole guest/window
exact. A second BG2-row experiment brought no improvement and was removed.
Evidence6412, qualification6413, publication6414. No full Destiny walkthrough,
new full-game/Genesis TAS, old broken-save compatibility or all-crashes claim.
The broad all28/Full MD/final Genesis TAS goal remains OPEN.


## Exile fixed native BG2 expansion:6420

Current6420 /installed-preview6417 fixes Exile black rectangles with SNES
backgrounds in a large window. Same launcher;501 choices/assets/helpers/user
settings retained. Binary e949d9c652ca32a5027722079c0586ab0bdec5a16991f137c8c0192360e18158.
Only pride_final_wide.obj changes against6414; previous Destiny/Timon/ride fixes
and every gameplay/audio object retained.

Exile C0044F native BG2 EF9128 decompresses3584 bytes (64x28 names). Upper
source rows have used columns0..32 and zero/unused33..63; lower rows use all64.
Captured native scroll is fixed0 through row151, then2/3/4/5 at152/160/176/200
in fixture6415. Extending the hardware512-pixel map exposed unused black
columns264..511. Reflect the fixed usable256-pixel canvas in added columns only,
guarded to the initialized native Exile BG2,8px tiles,rows0..151 and scroll0.
Do not repeat the entire level, foreground or lower scrolling bands. This is a
host artwork extension, not a new original plane or proof of general edge repeat.
Tall dominant-boundary-color policy and FullMD background are unchanged.

6418: old/new whole guest/nativePPU exact; only output bbox770,418..2558,874
changes at2560x1511/852x503. Canonical256 columns and lower bands exact. FullMD
window exact. LLE old/new guest exact; OriginalTiming compiled/LLE guest/native
exact (default Smooth compiled/LLE timing already differs in both old/new).
Actual paced150-field DPI-aware Windows capture inspected: rectangle gone.
Qualification6419/publication6420 pass; all501 actual launcher choices preserved.
No full-level walkthrough/final TAS or unrelated performance work. Broad goal OPEN.


## Graveyard and Exile lower-band presentation fallback:6430

Current6430 /installed-preview6427 adds the requested lower-background fallback
for Graveyard and Exile in tall windows. Same launchers;501 actual choices and
all installed assets/helpers/user settings retained. Binary
8a7e3114e5171adf3ec729bd8c295529ea6e88e82650bba4e7d4b7e9a535c7b9.
Only pride_final_wide.obj changes against6420; previous fixes retained.

Scene C003EB BG2 has uniform final64 rows160..223; C0044F final24 rows200..223.
Captured native bands6421 agree with the already-audited MD08C170/08C26E schedules.
In tall views continue these selected source strips below224, alternating vertical
reflection. Retain captured final-band scroll, map, palette and priority. Native
raster223 samples source224, beyond its28-row background: native BG2 PPM223 is
all black in both scenes. In tall views only, sample native222 at that join and
exclude the unused row from repeated strips (63/23 valid displayed rows). MD
keeps its complete64/24-row strip. Foreground and actors still compose normally.
This is an intentional expanded-picture fallback, not newly authored original
art, a new plane or a universal assumption about other scenes. Top edge remains
the existing dominant-color policy. Diagnostics report
background_extension=dominant_edge_color_with_reflected_bottom_band.

Per-draw64-row token cache decodes each reflected source row once for the current
width/column/source epoch. No actor/collision/camera/audio/gameplay changes.
Final6428: both scenes in native and MD background source controls preserve full
guest/nativePPU hashes. Only lower added area and native exposed join223 change;
rows through222 and entire native224-line windows remain exact. OriginalTiming
compiled/LLE same input guest/native/window exact. Both actual paced120-field
DPI-aware windows reviewed: themed ground/bones replace flat lower black areas
and the horizontal blank-border seam is gone. Qualification6429/publication6430
pass, all501 actual launcher choices preserved. No full-level/game/TAS rerun or
new performance guarantee. Broad all28/Full MD/final Genesis TAS goal stays OPEN.


## Initialization guard scope correction:6438

Current6438 /installed-preview6435 restores missing opening enemies. Same
launcher,501 actual choices/assets/helpers/user INIs retained. Binary
b430cd5aabc5386ee08f52f2a405bac95b16eeac6bd5e64ef9aa661874b59b9c.
Only pride_final_wide.obj changes against6430; all prior fixes retained.

Regression6414: LiveSpawnViewport required the normal player C3 controller
before widening every main-level initial scan. Pride's MD-selected activation
runs its settled-camera column rectangle BEFORE that controller starts. Its
rectangle shrank (columns0..42 instead of0..118 at this window); most opening
enemies in the expanded view were missed and the incremental scanner did not
recreate them.6431 actual6383/current comparison confirms the visible report:
working before has multiple ground/ledge enemies and pickup contexts; current
shows only one upper lizard. A prior stage/player/health-only fresh-entry test
was insufficient evidence of correct spawning.

Restrict the loading guard to adult6..9, the affected loader family. Cub0..5 and
bonus10+ retain established initial activation, including source-selected Pride
settled-camera scanning. Do not add actors or rescan/repair broken saves. Restart
level1 after reopening to execute its original initial scanner. An initial narrow
stack-context exception was superseded by this simpler scope correction; no
new guest opcode hook or source identity/header rewrite.

Final6436 fresh Pride at2560x1511/852x503 matches actual pre-regression6383 whole
guest/nativePPU/window AND all captured actor descriptor/positions exactly.
Ordinary walking/jump moves65->374 with4HP/2spares; actual paced DPI-aware Windows
capture reviewed with opening ground/ledge enemies visible. OriginalTiming
compiled/LLE30-field same-input guest/native exact. Fresh Destiny adult/player/
HUD/full view still initializes; guard behavior there unchanged.6437 qualification
and6438 publication pass, all501 actual launcher choices retained. No full-level/
game/TAS rerun or new FPS guarantee. Broad all28/Full MD/final TAS goal remains OPEN.


## Ride presentation and actor handoff:6464

Current6464 /installed-preview6460 fixes the three user ride presentation
reports. Same launcher,501 actual choices/assets/helpers/user INIs retained.
Binary3960f6a5cd786d21394094756dd713f9a1ffcdbc70900ed1988fc457ef43b834.
Only pride_final_wide.obj changes against6438; game camera source/object unchanged.

Actual copied slot1 host16947 is second ride near the exit, Simba3788/438,
6HP/6spares, camera3632/271, loop3408/travel7231. The future exit head is a
presentation preview, not a captured giraffe actor. C58D80 descriptor flags6A
and original live C07F59 pieces6Axx require horizontal flip40; the preview omitted
it. Future drawings now apply original descriptor horizontal/vertical flags,
including the head. The source/frame/palette choices remain independent.

At wide mounting the guest look goes395->127 then relaxes to selected48, about
80 updates. An experiment that changed guest framing immediately broke the
existing route and was discarded. Final ViewColumn changes ONLY the captured
s_frame.ram presentation for King rides wider than320; snapshot column is shifted
by excess look (slot1 -80). Live g_ram spawn/cull/camera remains column0 and all
original game operations/timing execute. Forecast visibility checks account for
this same output column. No CPU/game-camera change ships.

Preview removal used the script decision, before complete live sprite capture.
Recorded old gaps immediately before first nest8245, blue rhino8394 and pink
rhino8406 explain the oncoming blink. Search the original active script table,
including a bounded32-pixel just-due interval, and retain each body/branch preview
until its full original piece count is submitted. No actors, collisions, RNG,
script advancement or guest writes. Correct drawing order keeps live pieces above
the source preview. Original32-event/count64 guards and selected source sampling
remain. Candidate kept-piece VRAM substitution showed no staging mismatch in the
sample and was removed; do not broaden native sprite recovery based on this case.
TLK_RIDE_PREVIEW_TRACE now includes actual cursor, output column and flip flags.

Final6462: user head preview flags40/column-80, full guest/nativePPU unchanged.
Nearby normal route7400..10000 crosses both ride exits: complete guest/PPU exact
against published6435, end4653/457,6HP/8spares/checkpoint4720/480. All five body/
branch/nest handoffs now have preview on the field immediately preceding first
live submission. Original320x224 window exact; OriginalTiming compiled/LLE
user continuation exact. Three actual paced DPI-aware captures (two ride and
one user head) reviewed; capture names are threshold requests, not exact-field
video claims.6463 qualification/6464 publication pass and501 actual launcher
choices preserved. Existing slot1 works after reopening; no compatibility repair.

This slot is not the earlier missing-head opening case6445, which remains
unproven/open. No full King/game/final Genesis TAS or universal FPS claim.
Practical save replay: this native pause loop polls slowly. A2-field Start pulse
was missed;20 fields held then released resumes this save. Check pause and fresh
render-update counters before interpreting a stationary replay as game failure.
Evidence build/fidelity6462-ride-presentation-checks/report.json.


### Hakuna selected terrain/native materials6478

Actual slot2 host66106, descriptorC00481, frogC58E9C poseC3B22B at2040/413:
native scenery draws the MD physical shelf lower/absent. Same guest save with
MD foreground6470 supplies the ledge directly under the frog. Current cache
scenes-ea548b1d has equal225x71 MD/native grids (row450,map31950), matching the
independently checked scene correspondence. Enable existing per8x8 native
material adapter for level5 with selected MD terrain, exact grid dimensions and
native foreground. This concerns BG1 foreground geometry only; no BG2 plane,
layer/scroll/init/edge extension changes or assumptions were introduced.

The initial naive nearest-tile trial6473 changed intact trunks into leafy
patterns. Final6474 retains original native tile/palette/flips wherever flipped
opacity agrees with MD; differing shelves use existing alpha-weighted native
material match. Selected MD priority applies. Correspondence is an approximation
for version-specific art; do not report exact native material coverage globally.
Masks reset with scene cache and are only used for5;6/8 mapping is unchanged.

6476: old/new full user save and180-field resumed continuation guest/nativePPU
exact. MD foreground and SNES terrain controls window-exact. OriginalTiming
compiled/LLE exact. Real DPI-aware paused Windows client shows corrected ledge;
save-frame composed screenshot shows frog resting there.6477/6478 qualification
and publication retain501 actual launcher choices and all installed assets,
helpers/user INIs. No full Hakuna traversal or universal terrain/FPS claim.
Evidence build/fidelity6476-hakuna-ground-checks/report.json.


### Be Prepared mixed-terrain foreground6486

Actual user slot3 host97958 C004E5, Simba4732/528: original native foreground
differs from selected MD collision/layout with visibly broken shelves and gaps.
6480 MD foreground control draws complete shelf under Simba and correct vertical
rock edge. This uses the already independently reviewed305x45 equal world grids
and MD main PlaneA initialization/uniform displayed scroll evidence5771/5790.
Enable existing per8x8 native-material path for7 only with MD terrain and native
foreground, exact matching dimensions. Keep native original tile/palette/flips
where alpha agrees; nearest native material handles differing ledges. This is
an approximate art correspondence, not exact coverage for every MD-specific cell.
No BG2, layer/scroll/init, edge extension, guest, collision, camera or actors
are changed. Main Be Prepared only; dedicated summit recipe stays separate.

6484 full save and180-field leftward movement preserve whole guest/nativePPU
hashes, end4451/534,6HP/9spares. MD foreground and SNES terrain controls have
exact window pixels. OriginalTiming compiled/LLE exact; real DPI-aware Windows
client reviewed.6485 qualification/6486 publication preserve all501 actual
launcher choices/assets/helpers/user INIs;6487 prior Hakuna frog window exact.
Existing slot3 works. No full-level completion, universal terrain/material
accuracy, FPS or finalTAS claim. Evidence build/fidelity6484-prepared-material-checks/report.json.


## Return native-scenery performance6495

User's Simba's Return slowdown reproduced with current SNES-visuals/Genesis-
gameplay preset,2560x1511 window/852x503 canvas. Return native BG1/BG2 TM19,
TS0,CGWSEL0,CGADSUB19 and8x8 names require fixed-colour math, disabling the
previous native row/RGB shortcut. Cache per-layer palette results keyed by
choice epoch, brightness, all relevant fixed-math registers and CGRAM; decode
native BG2 tile rows once using unchanged actual name-table/scroll/flip/priority
addressing. Reuse those tokens in the original margin-occupancy test. Enable
native-material foreground tile runs in that fixed-math case and cache backdrop
colour separately. Subscreen blends and colour windows retain scalar handling.
No new art, plane equivalence, repeats, layer/scroll/init or edge policy.

Complete selected Return geometry does not use the native ring mirror test;
boundary-only tall BG2 rows and rows outside the world do not need unused ring
scans either. Final related Hakuna/Prepared user windows6496 remain exact.
Only wide renderer changes, no guest/update-budget/audio/camera/timing changes.

6493 old/new fresh1900 and genuine later encounter50876 guest/nativePPU/window
exact. Same normal-view unpaced median55.099->13.583ms,p9517.091ms. Actual paced
Windows client219/219 completed updates,58.26 wall updates/sec including the
capture; visible sample60.9. Maximum1024x768 sample99/99,median9.828/p9512.3ms.
The initial maximum trial18.47ms failed before off-world row work was omitted;
do not treat it as the final delivery. OriginalTiming compiled/LLE exact.
6494 qualification/6495 publication preserve501 actual launcher choices,
installed assets/helpers/user INIs; renderer only. No whole-level completion,
arbitrary-scene/all-PC60 lock or finalTAS assertion.
Evidence build/fidelity6493-return-performance-checks/report.json.


## Ending, fitted native bands and coconut lifetime6515

Current installed-preview6508 addresses three reproduced mixed-preset reports;
separate final Scar jump-away blink remains open pending representative save.
Shared summit/postfight C007DB now uses selected console camera width regardless
of free host update width. Actual60400->61450 old camera220 cropped Simba678
outside380-wide cinematic output; camera486 restores native Simba/platform.
Keep original camera step/streaming/scene scripts. Ending real window and native
sunrise63750 reviewed; no blanket claim about all Scar retreats. Nearby6512/6513
third-encounter replay showed the same attacks old/new and did not reproduce it.

Graveyard C003EB and Exile C0044F native BG2 have the scene-specific captured
224-row band schedules already audited6420/6430 (including Exile fixed152-row
upper canvas and changing lower bands). For tall native views, map output row
to that complete224-row picture and use THAT source row's own scroll/VRAM and
palette. Foreground/actors stay at their world coordinates. This replaces the
native tall lower-strip reflection with a full-picture fit; MD keeps its old
extension. Original224 rows (height224) and FullMD controls stay pixel-exact.
Existing Exile upper256 horizontal reflection retained. Diagnostics correctly
report native_banded_panorama_fit; no new art/plane/edge-repeat proof implied.

Gorilla's coconut factory was working: C58E84 appears for one submitted field
per birth in wide view, then its old C03BDB query deletes it against320-wide
bounds despite852 camera. Extend selected lifetime operand by actual camera
width minus canonical viewport (only when larger). Native/MD base window choice
and original carry/comparisons, vertical bounds, movement, impacts and deletion
remain. Actual neutral34900->35500 has6->1215 coconut draw records, and wide
ordinary damage outcome now matches console. Console guest/nativePPU/window
exact; OriginalTiming compiled/LLE short wide control exact.

6511 real Windows background/ending/fight captures viewed; current normal
180-field background windows approximately58.5fps including capture. Broad
all-resolutions/all-scenes performance or all-game/finalTAS acceptance not claimed.
6514 qualification/6515 publication retain all501 actual choices, assets,
helpers and user INIs. Only renderer, camera and coconut query objects change.
Evidence build/fidelity6511-playtest-report-checks/report.json.


## Actual King slot1 monkey/rhino source frames6529

User's new slot1 host17686 is normal King after second ride,6HP/6spares,
Simba4715/482 at checkpoint4720/480,852x503. Staging comparison6517 on neutral
180 fields proves original glyphs lose2031/146/78 nontransparent pixels for
monkeyC58B84/C58BA8 and rhinoC58C08 respectively; other staging differences are
not automatically new bugs. Diagnostic6468 King guest/nativePPU matches the
current player exactly. No whole-game source equivalence claim from that probe.

Original submitted pose/part source is already available from the native frame
metadata and captured ROM/WRAM art, including packed/mixed-size drawings. Factor
that decoder from existing ride source path; normal King known non-kept monkeys
and selected native rhino parts use those exact glyphs instead of stale VRAM.
Shared monkey frame pairs and live palette/flips/positions stay independent.
Rhino bodyC58C08 has no generic MD role; select body and headC58C14 explicitly.
MD rhino frame path, original kept native pieces, rides and other scenes retain
their existing behavior. No gameplay/animation/audio/background or priority edits.

Initial6519/6523 candidate fixed monkeys but generic role guard omitted rhino
body.6524 aggregate changed bbox was insufficient (another monkey).6525 documents
this, and final6527 requires the actual rhino-region pixels to change at17733.
Five phases17688/17708/17733/17735/17866 plus200-field movement keep whole guest
and nativePPU exact against6515; original256 and existing ride windows exact;
OriginalTiming compiled/LLE exact. Real DPI-aware window reviewed. Temporary
read-only source/priority probes removed; no broader priority adjustment shipped.
6528/6529 qualification/publication preserve501 actual launcher choices and all
assets/helpers/user INIs. Existing slot1 works. This closes the concrete monkey/
rhino corruption, not the earlier separate giraffe or Scar-retreat reports.
Evidence build/fidelity6527-king-animal-frame-checks/report.json.


## Recorded Graveyard ascent: tall black bands6537

Actual current slot2 is Graveyard C003EB,30707,3884/692,5HP/9spares. User's
preserved last_session.rec gives a genuine480-field ascent to4032/167, with
vertical view origin265->42. Read-only6533 row/black-pixel trace catches three
isolated native upload overruns: native forced blank3/10/12 rows at30850/31019/
31058 magnify into184/51/53 complete black game rows. Last native line remains
brightness15; these are not uniform world fades. Actual old/new pictures viewed.

Reuse nearest completed valid-stage line for forced-blank metadata in tall
initialized Graveyard only. Existing level0/1 policy unchanged. For Graveyard,
ordinary non-forced dark lines are returned directly, and an all-blank raster
has no replacement so stays dark. Preserve captured guest/PPU, layer/scroll/art,
camera, BG2 fitted band schedule, gameplay, actors and audio. No additional plane
or edge-repeat claims. Console-height view bypasses the extension.

6535: all three flash outputs lose their enlarged black rows; whole guest and
nativePPU hashes exact. Recorded480-field endpoint window/guest/nativePPU exact,
console window exact, OriginalTiming compiled/LLE exact. Real paced DPI-aware
ascent client reviewed; source-only read probe removed before production.
6536/6537 qualify and publish with501 actual launcher choices, assets/helpers/
user INIs retained. Water-boundary component of report remains unidentified:
current save is Graveyard, so ask which location/column/background is meant;
do not claim a waterfall fix or that the user supplied a wrong save.
Evidence build/fidelity6535-graveyard-blank-checks/report.json.


## Delivery6543: visible post-Stampede Scar scene

Current installed-preview6539, same launcher/501 actual choices, assets/helpers
and user INIs retained. SHA256
012812d63bf679b0916bb3dd415692c8930f788f09e0b9a8a0796d2f4bf69bb1.
Only host and bounded public resource-description objects rebuilt; frozen6225
frontend, audio and all other objects preserved from6537.

The mixed preset ran the Genesis cliff controller normally but CliffPaint
deliberately blacked every frame with SNES artwork selected. Like the existing
Pride illustration policy, show the sole prepared Genesis illustration under
that combination; log source_unavailable with the exact resource key. Browser
help describes the limitation. This does NOT implement SNES cliff artwork under
Genesis timing. The native SNES-timed transition remains unchanged.

6541 uses intact native23900 checkpoint5049 and neutral actual pad reads. Old
mixed output entirely black; new visible output equals old explicit Genesis
illustration, with exact whole guest/nativePPU hashes. Natural343-tick scene
finishes24367; Exile endpoint24480 guest/nativePPU/window exact. SNES-timed
negative and OriginalTiming compiled/LLE pass. Real paced Windows cinematic
capture viewed. No new background plane/edge-repeat, sound, gameplay or timing
claims. Evidence build/fidelity6541-cliff-visible-checks/report.json; publication
build/fidelity6543-cliff-visible-publication/report.json. Previous water-boundary
clarification and Scar retreat/giraffe-edge issues remain open. No full-game or
final TAS assertion.



## Delivery6551: real waterfall logs use the tall viewport

Current installed-preview6548. SHA256
9209ec2e71d8110fc164826c82242a618157b35599b1350a3f7d118ff50713c0.
Same launcher/501 actual resource choices/assets/helpers/user INIs retained.
Only pride_final_wide and one original generated C4part01 unit rebuilt against
6543; frozen frontend/audio/resources and previous fixes retained.

Report: waterfall logs have too small a drawing area and the top ones cannot
be seen. Native C48DF7/C58AEC wraps real log actors inside cameraY-40..Y+260
using a300-pixel displacement. Generic taller draw/spawn margins cannot widen
this separate loop. Extend its upper/lower bounds by VerticalMargins and grow
both wrap displacements by their sum. Original carry/ADC/SBC/flags, motion,
collision, wrap side effects, actor count and lifetime remain with the guest.
No painted replicas of platforms, no background changes. This intentionally
changes tall-view recycling; the same actor count travels a longer loop.
Console-height224 bypasses all four seams. New LLE pre-op hooks have matching
compiled forwards after the preceding original instructions; only this C4
unit needs recompiling. No framework/generated-source edits or ROM patches.

6549: untouched copied waterfall slot6465/66106, genuine20-field Start release
then neutral480-field continuation,852x503. Old visible logs stay below the
native upper bound; new real logs reach57 and19 while cameraY266/view-origin37.
Player1915/413,1HP/5spares unchanged versus baseline. Console whole guest/PPU/
window exact. Tall OriginalTiming compiled/LLE and real paced Windows endpoint
match; actual client viewed. No whole-waterfall traversal, unchanged tall-view
TAS route, universal platform density or full-game claim. Failed no-compiled-
forward candidate6545/6546 was never published. Evidence
build/fidelity6549-waterfall-log-checks/report.json. Prior water-boundary,
Scar retreat and giraffe-edge reports remain open; broad goal incomplete.



## Delivery6558: Be Prepared bats survive wide activation

Current installed-preview6555. SHA256
03c1deab311e5ba9eac6026194abcefc1bf354f88521b77ad91aea488a65fed8.
Same launcher/501 actual resource choices/assets/helpers/user INIs retained.
Only wide renderer and Be Prepared behavior objects rebuilt on6551. Frozen
frontend/audio/resources and all prior fixes retained; no extracted art changes.

Fresh level7 native loader checkpoint43000 from5240 and its unchanged original
per-poll suffix reproduce the report with the current mixed preset852x503.
Bat1264/256 is created43181, but at43182 its source-selected512-pixel distance
rule sees player745 and permanently removes it (distance519). Bat1376/208
likewise creates43210 and removes43211 against player857. Later bats repeat
the same pattern. Wide one-shot activation occurs before their original range.
This is live actor loss, not missing sprite metadata or a palette problem.

TlkWideActorInView reads the actual enabled expanded live viewport and its
current vertical margins. MD leaper retirement still takes its original branch
when beyond the512-pixel source range AND outside that viewport plus the
original96-pixel activation lead and32-pixel body allowance. The lead matters:
fresh actors can be80 pixels beyond the visible right edge. Keep real actors,
normal targets/wake thresholds, animation/motion/group rules and retirement;
no painted copies, global distance inflation or new user choice. SNES behavior
bypasses the adapter. Console-size viewport does not reach these far actors.

6556: old43400 has zero bat pieces/four lifetime observations; new has six
pieces from two real bats and327 observations. Continuing to43800 records956
observations including156 woken-state updates. Old/new positive guest state
intentionally differs because actors/RNG/damage now survive. Console and SNES-
behavior old/new whole guest/nativePPU/window exact. Tall OriginalTiming
compiled/LLE exact; paced Windows endpoint exact and actual client reviewed.
No C38E22 attack callback occurs in the sampled encounter (also none in the
console control): do NOT label this complete attack coverage. First failed
32-pixel-only margin candidate was not published. This turn's three completed
final-binary observations were reused while finishing the remaining checks.

Restart Be Prepared after reopening the launcher: an older in-progress save
whose spawn was already consumed cannot recreate removed bats by drawing.
Evidence build/fidelity6556-bat-lifetime-checks/report.json; qualification6557,
publication6558. No whole-level traversal, full-game/TAS or FPS claim. Other
pending reports remain open and the broad goal is incomplete.



## Delivery6570: stable blue-bug pickup flight position

Current installed-preview6567. SHA256
2635970c05859d14f94be9f40221c8c4d96092e2571c5d9454b13ff8ffe72b9f.
Same launcher/501 actual choices/assets/helpers/user INIs retained. Only wide
renderer object rebuilt on6558; all earlier fixes and frozen objects retained.

Actual new user slot1 copied6563 is Pride host10175, player274/412,6HP/8spares,
checkpoint656/592,852x503. It ALREADY contains the collected blue bug's left
HUD flight C58951/C55413, position123/38, poseC528DD. User recording after the
save is all neutral while paused. Preserve original slot/settings/recording;
use a normal20-field Start hold/release to observe the remaining flight.

Native draw pieces span X115..139, whose inferred HUD side is initially0.
ScenePieceShift treated this fixed effect as vertically centred in the tall
window. When the flight moves left and gains a nonzero inferred side, the same
effect becomes top-anchored. That is a visible139-game-pixel relocation in the
503-row view, unrelated to native sprite pixels or gameplay flight motion.
Recognize strict common pickup-flight ownership before generic fixed-piece
coordinate/side heuristics and retain top HUD anchoring throughout. Shared
role applies to both flights across supported scenes; no level-specific patch.
Keep original-height drawing, popup positioning, source choices, flight/game
logic, camera, native PPU, sprite artwork, palettes, audio and timing unchanged.

6568: three actual remaining-flight samples10177/10179/10183 have identical
whole guest/nativePPU hashes old/new. Realigned first flight image reviewed;
console224-height window exact. OriginalTiming compiled/LLE exact, completed
flight10275 guest/nativePPU/window exact. Actual paced Windows paused-flight
client reviewed with the bug at the HUD top. Original user slot works directly.
An exploratory MD-popup-offset change was removed before final build; popup
positions remain unchanged and its failed source-control probes are not passes.
No new background layer/edge/scroll claim or full-game/TAS/FPS assertion.
Evidence build/fidelity6568-pickup-anchor-checks/report.json; publication6570.

Scar missing-final-fight report remains OPEN. User clarified Pride Rock, but
the slot4 inspected6559 was Graveyard opening4772.6561 current-wide nearby
Pride Rock route reveals a live second Scar, then stalls before the last fight;
it does not reproduce an absent final Scar or qualify the summit. Recheck save
timestamps before asking for the corrected encounter save on continuation.
Broad all-levels/FullMD/finalTAS goal remains incomplete.



## Delivery6578: early King animals use initialized native colours

Current installed-preview6575. SHA256
d537248fbdd0c34022f3c9483b0118db1cc1b0ef6c50df78f2165f20d873cfc6.
Same launcher/501 actual choices/assets/helpers/user INIs retained; only wide
renderer rebuilt on6570. All previous fixes and frozen graph objects retained.

Actual new user slot2 copied6571: King host15264, player67/397,6HP/8spares,
checkpoint67/387,852x503. Off-native monkeys/heads can render before their own
native palette upload. Monkey OBJ2/3 still exactly contain initial scene banks
50BBC/50BDC, not their initialized602F7/60317 banks. Rhino head OBJ5 still has
50C1C while its body owns50B9C. This produces the reported neon monkeys and a
rhino head whose colours disagree with its body. Native palette fingerprints
alone identify valid scene data but do not prove ownership for a far actor.

Under normal King, a validated original source piece, captured monkey/head
owner and exact initial-bank match now recover the original native animal
palette. Initialized banks, later palette changes and flashes keep captured
CGRAM. No approximate colours, guest writes, actor/animation or source-choice
changes. Existing giraffe recovery remains; MD palette selection unchanged.
6578/palette-evidence.json verifies all four original ROM bank operands against
the actual saved raster and genuine180-field rightward continuation. First
motion attempt incorrectly pressed Start on an already unpaused save and was
discarded; the retained continuation uses25 neutral fields then100 Right.

6576: corrected monkeys/rhino head visible in actual paced Windows client.
Guest/nativePPU exact. Selected MD console framing is320 wide: its extra64
columns legitimately show the corrected head, while original256 columns are
exact. Explicit MD-palette old/new output exact. After normal initialization,
180-field continuation whole guest/nativePPU/window exact. OriginalTiming
compiled/LLE exact. User slot2 works without a restart. No new background
planes/scroll/edge, complete-renderer, full-game/TAS or FPS claim.

The second half of the report, palette change not behaving correctly, remains
unclassified: async clarification asks resource-menu SNES/Genesis switching or
changes during gameplay (possibly sunrise or monkey reaction). Do NOT claim
an unspecified second palette problem fixed; preserve the normal live change.
Scar final-fight report remains OPEN. Slot4 timestamp was observed updated to
2026-11-18 13:51 during this audit; re-read it next rather than assuming the
earlier Graveyard4772 copy is current. Broad goal remains incomplete.
Evidence build/fidelity6576-king-colors-checks/report.json; publication6578.



## Delivery6583: independent King sunrise transition

Current installed-preview6580. SHA256
4594b91fd077fffad3860c93bc5b4e0d6f97cebd3e2d9dfe5a2795d05eb2918c.
The user clarified that slot2's second palette report means the sky/world
sunrise during gameplay, not changing the resource-menu colour selection.

Original native C0D178 swaps the512-byte C601B5 palette when X>=108 or Y>=480.
Original MD18D79E/18D816 instead moves RGB3 channels by one every nine completed
updates. The mixed SNES-art/MD-gameplay preset formerly used the immediate
native scenery swap. New Gameplay / Levels / Can't Wait to Be King / Sunrise
transition inherits the gameplay parent, independently of scenery/sprite colours.
SNES timing keeps the immediate change; Genesis timing keeps the existing saved
MD controller. Native scenery colours approach the original C601B5 BG target
from C50B7A by up to four RGB5 units per step. This is a mixed-source adaptation,
not a claim the native original fades. Backdrop0 starts at native forced black.

Palette evidence: initial native BG bytes1..127 verified against actual intact
slot2 PPU0; original palette-event oracle and MD write-trace evidence retained.
An initial inferred50A7A base was wrong: actual screenshot revealed green
scenery; discarded before qualification and corrected to50B7A. Captured entries
not equal to the target stay live, preserving other per-row effects. Native
CGRAM, NPC palettes, actor triggers/movement, audio, King BG1/BG2 maps, layers,
scroll and edge extension unchanged. MD colours with SNES timing use settled
original MD palette at the trigger; sprite palettes keep their own live clock.
No new renderer-completeness/background-capability claim.

6581 uses the intact native backend payload of actual user slot2, same ordinary
25-neutral/100-right continuation. Four samples include the gradual middle and
identical daylight endpoint. Whole guest/nativePPU hashes exact old/new;
SNES timing reproduces the previous window exactly, MD-colour old/new output
exact, compiled/LLE exact. A new-build mid-fade full save resumes identically.
Actual paced Windows client reviewed. No full-game/TAS/FPS claim.

All501 prior launcher choices remain resolved identically; one live choice added,
502 total. Prior fixes, frozen audio/host, extracted assets, helpers and user INIs
retained. Renderer, bounded public resource catalog and browser-description
object rebuilt. IMPORTANT: previous-build FULL saves reject the new source
catalog; original files are untouched. Restart/re-enter a level and make a new
save; no compatibility migration requested or attempted.

Scar final-fight report remains OPEN, re-read newly updated slot4 on continuation.
Broad all-levels/FullMD/final Genesis TAS goal remains incomplete.
Evidence build/fidelity6581-sunrise-checks/report.json;
build/fidelity6580-sunrise-player/palette-evidence.json; publication6583.



## Delivery6597: slot4 wide ostrich-entry handoff and head audit

Current installed-preview6594. SHA256
0fd6c00f5419fdbbebc0e1eb74cda50171ad9663cbbd5f9d1f249e4db33f525e.
Same502 choices/assets/helpers/user INIs. Renderer-only rebuild on6590;
all previous animal/palette/sunrise fixes and frozen graph objects retained.

Actual slot4 copied6591: King30767, Simba2131/331,6HP/6spares,852x503,
paused. Use ordinary20-field Start hold/release to continue. This actual save
also comes from the earlier501 catalog; intact native backend payload used,
never modified headers/WRAM/identities. No additional source-catalog restriction
introduced by this renderer change.

HEAD: native descriptorC58D80 points to flat tilted poseC07F59 with flags6A.
All16 actual saved head parts belong to original world2080/304. The source7
image/origin audit4709 and direct original bitmap inspection match that tilted
pose. No arbitrary head displacement, pose replacement or gameplay contact
change. As entry retires this actor, a wide view can still show its painted
BG1 neck. Retain the last captured original head, anchor and flip as a visual
ride preview until it leaves the expanded handoff view. Uses independent
SNES/MD frame/palette choices; no retained actor or phantom platform.

CAMERA: original selected ride still uses320 coordinates. On entry the native
camera correctly rebases1783->2052 and look394->127. Previous presenter also
applied a negative look correction as soon as A56 became nonzero, exposing an
abrupt wide-window jump. Completed first-entry raster still has BG1HScroll247
from camera1783 while RAM has advanced2052; unwrapping against RAM incorrectly
chooses2295, the adjacent512 ring. Use the last producer camera for that owned
entry raster, then retain measured pre-handoff framing and converge over512
pixels actually ridden. Projected completed camera now1780->1783->1795,
while whole guest/nativePPU remain identical. No guest camera, travel accumulator,
script, collision, actor, audio or source-choice modification.

BACKGROUND EVIDENCE: King native BG1 is the authored foreground/ride ring;
native BG2 is the existing independent512-wide panorama. Native BG2's captured
entry phase236->272 is retained separately, then converges with the same travel
weight; do not assume it has BG1 scroll. MD scenery continues to use its own
original per-band sampler at the projected camera. No plane correspondence,
new layer, edge-repeat or complete-renderer capability assertion.

Pointer-free presentation history13,444-byte header adds nine bounded fields
for camera/source phase/loop and captured head. Previous histories still read;
new current-source saves preserve mid-handoff continuity. No synthetic attempt
to reconstruct an already completed transition from old raw-native history.

6595: same genuine neutral continuation, seven before/entry/settled points;
whole guest/nativePPU old/new exact. OriginalTiming compiled/LLE exact, console
window exact, mid-handoff current save resumes with exact world image and hashes.
A one-pixel HUD edge differs between raw-native and full-presentation restores,
outside the reported issue and deliberately not pursued. MD background choice
retains identical guest state. Actual Windows handoff reviewed; retained entrance
head confirmed in the30829 preview. No all-rides/full-level/full-game/TAS claim.
Broad goal and missing final Scar report remain OPEN; slot4 is now this King
entrance, so recheck actual save contents before pursuing the earlier Scar report.
Evidence6591 user copy,6592 original observation,6595 checks,6596 qualification,
6597 publication and source-evidence.json.



## Delivery6605: missing giraffe heads and expanded-view neck joins

Current installed-preview6602. SHA256
86e1cab098b0112396d74eff11927938ff585b3987b51c19134193444377a0b5.
Renderer-only rebuild on6597, same502 choices/assets/helpers/user INIs. Current
user saves1/2 load unchanged as FULL current-source saves; no new save schema,
source-catalog or installation-data change. All prior frozen graph objects,
sunrise, King palette/source and ride-handoff fixes retained.

Actual user saves copied6598: slot1 King13292,666/289,camera240/123,8spares;
slot2 King15018,756/289,camera346/133,8spares; both paused,852x503. Slot1 has
native counter140 and a live linked C58D70 head1032/289 whose whole13-part draw
was skipped. Its previously captured piece list stays missing even while paused.
Generalize the established rhino draw-budget seam to all three giraffe owners.
A source-validated completely absent initialized head also rebuilds in paused
snapshot presentation, with reciprocal ownership, active-chain, original7-pose,
hidden/blink/fixed guards. No actor, OAM, VRAM or budget writes. Source choices
remain independent; far-edge missing MD artwork is recovered too.

CORRECTION TO PRIOR HEAD CONCLUSION: source coordinates alone were insufficient
proof of a clean visual join. The common mirrored bending endpoint C58D70 uses
the same flat C07F59 drawing as C58D80, but its original initializer adds8/1
(C18F14/C18F1E), while the static initializer adds6/0 (C18F71). The exact native
BG1 neck tile patch at656..696 /304..336 matches the static neck after1424/16
translation (30 original tile words). Static native2086/304 therefore maps to
662/288, versus this dynamic actor664/289. Expanded native-art/native-scenery
presentation aligns that endpoint by-2/-1. This is a deliberate visual attachment
adaptation for the revealed wide view, NOT a claim the original program used
different actor coordinates. Standing/intermediate poses, MD head artwork and
console-size view keep their existing positions. Static heads with MD contacts
restore the omitted native artwork X+6, including captured entrance/exit previews.
Native OAM columns and extra columns use the same complete-head transform;
physical actor/platform/contact positions are untouched.

Background evidence is native BG1 authored neck material, not BG2 or a new
plane equivalence. No map/layer/scroll/edge-repeat or renderer-completeness
claim added. Original native6088 replay/reference6601 confirms the static
flat-head presentation; a staged-VRAM diagnostic showed the existing sprite
decoder was not this attachment issue and was removed. Backtrack probes did not
produce a full visible dynamic flat-head reference; do NOT claim they did.
The attachment proof is the exact source tile/initializer correspondence above.

6603 checks: both actual full paused saves retain whole guest/nativePPU hashes;
slot1 missing head0->13 parts immediately on load. Two genuine Start/resume
windows preserve hashes/gameplay, console window exact, resumed OriginalTiming
compiled/LLE exact. Already-visible MD head source/placement exact; its formerly
missing far-right neighbor now appears, so whole MD window intentionally differs.
Two actual paced Windows clients reviewed and paused join crops reviewed.
6597 ride-entry continuation guest/nativePPU remains exact with static attachment.
A too-broad MD whole-picture assertion was corrected to the actual unchanged
head region; existing timestamp-validated runs reused, then the remaining real
window/source checks completed without repeating unrelated replays.

No all-head-art combinations, all-scene/FPS/full-game/TAS claim. Broad goal and
missing final Scar remain open. Current slots1/2 are these King giraffes; slot4
remains King entrance, not the earlier Scar report. Preserve actual timestamps.
Evidence6600 original source archive,6598 actual user copies,6603 checks and
attachment-evidence.json,6604 qualification,6605 publication.



## Delivery6616: ride rhino ear ordering and disappearing ostrich

Current installed-preview6613. SHA256
60cbfbf77bd42135edd60b06a933b1057910392d591bc8d01362434aabc1d4cc.
Renderer-only rebuild on6605, same502 actual launcher choices, assets, helpers
and user INIs. All prior frozen objects and giraffe/sunrise/handoff fixes retained.
Actual current full user saves3/4 load unchanged; no schema or catalog change.

Actual copies6606 slot3 King26308 and6611 slot4 King26668, paused852x503.
Pink rhino: all9 original glyph parts exactly match staged VRAM and all1050
opaque pixels are visible in the paused real actor. The missing ear is instead
in the next preview after resume. Its branch visual child was drawn ahead of
the co-located ground rhino. Actual native submitted order at26428 is collision
parent slot42, ground rhino44, visual child53. Preview now follows that order
per event, preserving all positions/poses, event order and independent artwork
choices. Original ear28/28 source pixels now visible in the overlap. No BG1
priority change, new glyph or scenery/layer/edge-repeat assumption.

Slot4 bird is alive at1979/444, ownerC58C20, poseC1D788. Original camera1903/147
puts its full box top227 below the224-row native draw area, while the taller
bottom-anchored world[-7,496] still includes it. Recover only a fully omitted
live source-owned ostrich with its current original pose, reciprocal packet,
active-chain, hidden/blink/fixed guards, wholly outside original camera and
intersecting tall view. Uses existing three-owner/38-pose metadata; only the
current first owner was played in these checks. Exact source glyph recovery
avoids stale VRAM. No retained synthetic actor/animation, native vertical cull
widening, spawn timing, camera, gameplay, OAM or audio change.

6614 checks: paused full saves plus short genuine Start/resume windows preserve
whole guest/nativePPU hashes. Missing bird0->18 parts immediately, then returns
to ordinary native submission when original camera includes it. Console window
exact; resumed OriginalTiming compiled/LLE guest/nativePPU exact. Known tiny
right-HUD edge host differences were recorded, not pursued as ride defects.
Source ear pixel/OAM evidence, MD-art control and two actual paced Windows
client captures reviewed. Existing identical command/binary timestamp-validated
runs reused after correcting overly broad whole-host-picture assertions.
No all-rides, whole-game/TAS or global FPS claim. Broad goal and earlier missing
final Scar report remain OPEN; current slot4 is King bird, not that Scar save.
Evidence6608/6612 archive original sources before mutation,6607 motion/actual
OAM,6614 checks/source-evidence.json,6615 qualification,6616 publication.
Ear-only6609 diagnostic was never published.



## Delivery6623: second-ride entrance ground strip

Current installed-preview6620. SHA256
86c2f9b667a55c4c59ebaa6a22aa3941ba94930b2250c6d026e6f2721920bb4f.
Renderer-only rebuild on6616; all502 actual launcher choices, assets, helpers,
user INIs and current full save1 preserved. Earlier bird/ear/head fixes retained.

Actual copied6617 slot1 King5813, paused852x503, immediately before the second
ostrich ride. Genuine Start/resume6618 reproduces a flat orange bottom strip
under the hippos/giraffe appearing at the ride entrance. Root cause is a
special last-row BG1 predicate using cumulative A58 from both rides, while all
other rows use current ride A40 versus camera-A56. At5853 camera3591,loop3408,
A40=21 but A58=4608; at5873 camera3682,A40=112,A58=4608. Neither is locally
wrapped. Original live BG1 map last row480 has different authored entrance and
road cells (at3352 value15912 versus3864 value15536). Sampling the road there
prematurely replaced water/entrance silhouettes with a flat strip. Remove that
last-row override in both pixel addressing and512-column row-token reuse;
use the same local wrap predicate for the entire road. At5933 camera3466,
A40=408,A58=5120, local wrap is real and old/new world picture is unchanged.

Scene evidence is original King BG1 level map and existing authored512-pixel
ride ring; no BG2 initialization/scroll/layer or edge-extension policy changes,
no plane equivalence or full-renderer capability claim. No guest/OAM/VRAM,
spawn, collision, camera, audio, catalog, schema or asset change.

6621 checks retain whole guest/nativePPU and gameplay at5853/5873/5933.
Differences before the wrap are exactly in the bottom48 host rows (16 source
rows); known small top-right HUD-edge host differences excluded from unchanged
world-picture controls. Paused pre-entry and already-wrapped first-ride world
pictures unchanged; resumed OriginalTiming compiled/LLE guest/nativePPU exact.
Actual paced client viewed; initial1-second capture was still before boarding,
so later1.6-second capture actual-corrected-entry.png also taken and reviewed.
No unrelated/full-level/game/TAS/FPS checks or claim. Broad goal and earlier
missing final Scar report remain OPEN. Current slot1 is this second entrance.
Evidence6617 copied user save,6618 reproduction,6619 source archive before edit,
6620 candidate,6621 checks/source-evidence.json,6622 qualification,6623 publication.



## Delivery6630: pink ride rhino preview-to-live position

Current installed-preview6627. SHA256
d458eacc4e6fafb2a4e833643a09ec05a4e82e0da0332042896170708105e4e0.
Renderer-only rebuild on6623; same502 actual launcher choices, assets, helpers,
user INIs and current full save2 load unchanged. Earlier ground/ear/bird fixes
retained; no save schema, catalog or extracted asset change.

Actual copied6624 slot2 King7550, paused852x503, second ride. Neutral resume
falls at the immediately approaching low branch. Genuine Start plus Down passes
that branch and reaches the reported pink rhino. Trace6625 reproduces a visible
16-source-pixel sideways jump when preview becomes live: old final preview
at7588 has world3836, original first live at7589 has world3852. At7588 script
C0B625 compares actual A40=2399 plus64 lead=2463 against MD event2460. Current
camera3409 floors to3408, selected original offset380 plus lead64 yields3852.
Interpolating directly to exact event distance rounds to the previous16-pixel
tile. This is visible48-host-pixel displacement at user's3x scale, not a
one-frame transition/hash-only correction.

Preview now forecasts existing selected MD camera arithmetic on bounded local
copies, retaining current look/fraction and ordinary four-pixel riding motion,
then applies original16-pixel spawn flooring. Camera/player512-coordinate wraps
are equivalent translations, preserving unwrapped phase. Just-due packets use
that same four-pixel cadence while awaiting their first submitted drawing.
SNES-camera preview path is unchanged. All obstacle shapes share this placement;
no rhino-only constant shift or live collision/actor offset. No guest CPU replay,
guest/OAM/VRAM writes, camera/spawn/physics/audio changes or additional state.
Forecast is bounded to256 steps; farther entries retain existing distance math.
No new claim that future player collisions or changing warning state can be
predicted exactly, or that all ride/camera combinations have been played.

6628 checks: three old/new genuine resumed save pairs retain whole guest/
nativePPU and gameplay; new final preview and first live both3852. Earlier
preview4364 minus the original512 camera wrap equals3852 too. Paused pre-resume
world picture and isolated native-camera controls unchanged; MD-art preview
keeps3852; resumed OriginalTiming compiled/LLE guest/nativePPU exact. Actual
paced Windows client reviewed around the handoff. No unrelated full-level/game/
TAS/FPS run or claim. Broad goal and earlier missing final Scar report OPEN.
Current slot2 is this second ride, not previous giraffe/Waterfall saves.
Evidence6624 current user copy,6625 reproduction/preview.csv/script.csv,
6626 original-source archive before edit,6627 candidate,6628 checks/source-
evidence.json,6629 qualification,6630 publication.



## Delivery6638: blinking King monkeys in the expanded view

Current installed-preview6635. SHA256
744c23e4b1e30594bd0ee9fa5f242bc2413e7d7bb869e7a33aeccdff1997a5d0.
Renderer-only rebuild on6630; all502 actual launcher choices, assets, helpers,
user INIs and current full save3 load unchanged. Earlier ground/preview/ear/
bird/head fixes retained; no new source catalog, schema or extracted assets.

Actual copied6631 slot3 King11433, unpaused852x503. Player4716/411,
camera4322/271. Reported top-right pink monkey is live C58BFC at4976/96.
Sparse neutral endpoints11437/11445/11460 had complete8/9-part drawings and
therefore missed the actual refusal. Paced real-window reproduction6632 and
temporary private diagnostic6634 identified omitted intervals. At11451 and
11505 this monkey has0 submitted pieces while total captured list is125/126;
these totals exclude HUD/native accounting and are NOT the original budget.
Source C0A6A2 refuses its whole draw when original counterAD has reached127.
Other monkeys later in the original actor queue are omitted too. No palette,
VRAM glyph or background-priority bug was established. Temporary pixel/compose
diagnostics were removed completely before the final build;6634 never shipped.

Extend existing RecordKingAnimalBudgetIntent at C0A5ED (rhino/giraffe recovery)
to16 known King monkey descriptors and30 source-validated poses. Existing seam
is after original visibility/blink and horizontal admission; source refuses the
whole glyph queue next at127. Append exact current pose parts using existing
OriginalPieceSource/WRAM decoder. Preserve animation, flips, palettes, actor
order and native rejection outside the view. No live OAM/counter/uploads/guest
writes, retention/frozen animation or gameplay change; no new paused-save
reconstruction claim. This current save is already unpaused.

6636 checks: old/new guest/nativePPU and gameplay exact at three neutral
endpoints. Missing11451/11505 target0->8 parts, with5022/4923 pink host pixels;
already-visible11445 subject crop unchanged (9 parts,5013 pink pixels).
OriginalTiming compiled/LLE guest/nativePPU exact; independent MD-art control
also recovers target. Paced actual client reviewed through short animation
window, budget.csv records actual127+ refusals and recovered current poses.
Recovery also reveals later missing monkeys at their real positions. No new
BG layer/scroll/edge/capability claim, unrelated all-game/TAS/FPS tests or claim.
Broad goal and earlier missing final Scar report remain OPEN. Current slot3 is
this King monkey layout, not older rhino/Exile/Waterfall examples.
Evidence6631 current user copy,6632 motion/paced reproduction,6633 exact source
archive before mutation,6634 discarded private diagnostic/source,6635 candidate,
6636 checks/source-evidence.json,6637 qualification,6638 publication.



## Delivery6654: visible Graveyard vulture before damage

Current installed-preview6651. SHA256
6632507c3ae84edfbf3ad08c166ec57a425fbaf029bbc585aceee242adce396a.
Only pride_final_wide.obj rebuilt on6646; Hunt RAM-work budget and all earlier
frozen gameplay/audio/host objects retained. Same502 actual launcher choices,
assets/helpers/user INIs and current full slot1 load unchanged. No new schema.

Actual copied6647 slot1 Graveyard55161, paused852x503, Simba3471/432,
camera3067/329,3HP/7spares. Genuine Start plus neutral input reproduces3->2HP.
Read-only private probe6649 identifies exact attacker at55171: taskB593,
descriptorC58CCA,3444/474, actionC17911, packetDCDF, current poseC3F17D.
Packet flags803A include high hide bit80, so C0A548/A54B skips it before any
draw bounds/parts. It has no submitted pieces although source collision remains
active. Initial bird3390/481, poseC3F083, is already wholly right of original
256-column picture (source bbox starts3354, camera right3323) and belongs in
the expanded view. This establishes the missing attacker, not which earlier
source operation set the packet's hide bit; do NOT claim that setter was traced.

Expanded-view presentation recovers only a completely omitted, live owned
vulture with that hidden bit, positive original health at actor+2A (initializer
C16DA0 stores it), current flying C173E7/C17911 action and role-validated pose.
All five known Graveyard vulture descriptors share the guard. Active task-chain,
reciprocal packet/position/pose checks and original blink/fixed exclusion remain.
Complete source box must be outside original256x224 picture. Append existing
exact current source parts; never clear guest hide bit, retain an actor or
synthesize animation. Native source glyphs are read from their original ROM
rather than unadmitted VRAM; independent MD artwork uses its existing adapter.
Helper renamed NativeAnimalPieceSource to reflect its broader animal ownership.
Console view, damage, collision boxes, AI, physics, sound, OAM and guest state
remain unchanged. No background layer/scroll/init/edge/capability changes.

6652 checks: paused warning0->24 parts, pre-contact0->21 and after-contact0->20.
All three old/new full guest/nativePPU/gameplay pairs exact; health3 before and2
after the same contact. Paused actual Windows client reviewed: complete bird
approaches the hanging Simba visibly. OriginalTiming old/new/interpreted guest/
nativePPU exact; independent MD-art recovery works; console window exact.
The private damage observer is neutral against production hashes. A short
right+jump attempt still takes the imminent hit; no successful escape claim.
An initial candidate used actor+2C as health and missed the paused bird; source
initializer review corrected this to+2A before qualification/publication.

No whole-Graveyard/all-enemy/full-game/TAS guarantee. Other hidden action types
and partly original-screen hidden packets are deliberately outside this repair.
Broad source-coverage/all-level/final unchanged Genesis TAS goal remains OPEN.
Current slot1 is this Graveyard wall, not older King ride examples. Evidence
6647 actual copy,6648 reproduction,6649 private exact attacker probe (not shipped),
6650 original-source archive before mutation,6651 candidate,6652 checks,
6653 qualification,6654 publication.



## Delivery6664: Graveyard liquid beneath columns in tall views

Current installed-preview6661. SHA256
 d9482e91aab2d4db56a36eee7c7cff3cfd9951278f22464fa317c80ddf3a9f46.
Only pride_final_wide.obj rebuilt on6654. All earlier frozen gameplay/audio/
resources/host/update-budget objects retained. Same502 actual launcher choices,
assets/helpers/user INIs and full current slot2 load unchanged; no schema change.

User clarified missing green liquid beneath the right Graveyard columns,
not general scenery across the bottom. Actual copied6655 slot2 at124226,
852x503 view, player4015/432, camera3308/323, two columns4032/487 and4080/487.
FactoryB513/C58D44 actionC2D1D3 owns primaryDD23 and secondaryDD45 via actor+28.
Source C1CC50 clamps generated dynamic frame7EAB06 to208 pixels, while C2D35A
places its top using the full live actor+2C height249 and actor+5E base736.
Thus picture stopped41 pixels above its actual base when exposed by tall view.

Tall-view compositor appends only missing original alternating32-pixel tail
rows from each correctly owned current factory draw, up to its actual base;
last partial row is clipped. Existing52 pieces remain exact and12 are added,
with original tile/phase/slot/palette/priority and no duplicate packet/local
positions. Independent complete MD artwork uses that same real base. Source
208 cap/RAM/OAM/VRAM/collision/gameplay remain intact. Original-sized view exact.
This is an existing liquid sprite tail repair, not a horizontal pool texture
or a newly reconstructed background plane. No scenery layer/scroll/init/edge
or capability reporting changes. Generic bottom background fill is separate.

6658 unmodified original Genesis replay to16241 and6659 original native replay
16390 show green liquid under these columns; earlier6657 source-control report
predates clarification and is superseded by6662. Do not use a different camera
location as proof the water is absent. Decoded assets alone were insufficient;
source constructor/position logic and exact-location references establish it.

6662 checks: full paused old/new guest/nativePPU/gameplay exact, original52
pieces exact, both factory draw owners verified, source repeating tile and
screen/local deltas exact, no duplicates. Independent MD artwork reviewed.
Console old/new picture exact. Paused OriginalTiming old/new/LLE hashes exact.
Short genuine Start+Down old/new gameplay/hashes exact (imminent death, not a
successful traversal). Actual Windows paused client reviewed with restored
liquid through base. No all-level/performance/complete-scene/final-TAS claim.
All-level/full-MD/final unchanged original Genesis TAS goal remains OPEN.
Evidence6655 actual save,6658/6659 source,6660 historical source archive,
6661 renderer candidate,6662 focused checks,6663 qualification,6664 publication.



## Delivery6671: Exile upper terrain after source-memory reuse

Current installed-preview6668. SHA256
f6d218528685b28b98e207dbf2654ec17acf20ecd5d7617fbd04a32cb3d93825.
Only pride_final_wide.obj rebuilt on6664. Earlier frozen gameplay/audio/resource/
host/update-budget objects retained; same502 actual launcher choices, installed
assets/helpers/user INIs and full current slot3 work unchanged. No schema change.

Actual copied6665 slot3 Exile72391, C0044F, 852x503 view, Simba1424/2432,
camera748/2255, origin1977, native_row279,1HP/6spares. Top167 logical rows
show scrambled foreground. Native PPU picture itself is intact. Exact current
RAM7F0000 prefix30848 bytes equals the independently decoded original graphics
streamDEAE73. Cached map has26885 bytes of the same graphics followed by exact
original terrain from descriptor+9/DBC845; map dimensions200 bytes by155 rows.
The original scene reused map memory for graphics while its streamed native
foreground remained displayed. We did not trace the caller that loaded this
bank: exact byte identity proves its content, not that setter or sprite role.

LevelOf now recognizes this exact complete graphics bank only in initialized
Exile C0044F. A bounded cached decoder gets the original descriptor map; a
renderer-owned view substitutes only the overwritten prefix and preserves the
remaining live map bytes. No guest/map/RAM/VRAM writes or gameplay changes.
Existing source tile dictionary, current graphics/palette, priority and world
anchors remain in use. Native original-sized output and selected MD scenery
are unchanged. This is foreground-map provenance, not BG2 layer reconstruction;
no layer/scroll/initialization/edge/capability reporting changes were made.
Partial loads and different reused banks are outside the full-bank guard.

6669: loaded and60-field neutral continuation old/new guest/nativePPU/gameplay
exact. Native console old/new picture exact; MD foreground and fullMD artwork
old/new pictures exact; OriginalTiming old/new/LLE exact. Real paced Windows
client reviewed with complete upper terrain. Loaded picture diff bounded to
(2,1)..(2558,502) of2560x1511; all lower pixels unchanged. Neutral continuation
keeps Simba at the same position; do not call it a full traversal. No whole-
level/performance/full-game/finalTAS claim. Broad goal remains OPEN.
Evidence6665 actual copy,6666 exact source-bank/map evidence and artwork controls,
6667 pre-edit archive,6668 renderer,6669 focused checks,6670 qualification,
6671 publication. No generated game code, recordings, ROMs or extracted assets
added to maintained sources; renderer decodes the installed source map once.



## Delivery6677: Hakuna native background in tall windows

Current installed-preview6674. SHA256
5cfae26d6e2f29248cab0c50ed5674c17dfa124be4549a218f6b5210add4ec3a.
Only pride_final_wide.obj rebuilt on6671. Earlier frozen gameplay/audio/resource/
host/update-budget objects retained. Same502 actual launcher choices, installed
assets/helpers/user INIs and save schema retained; no shared build-graph rebuild.

User confirms flat color bands/cutoffs above or below mountains in Hakuna.
Current preset native artwork/MD gameplay at852x503 used single dominant-color
extensions around the original224-row background: opening263 extra bottom rows,
waterfall229 extra top/50 bottom. These produced large flat areas and abrupt
cutoffs. Scene C00481 now uses the same captured-picture vertical fit as existing
Graveyard/Exile: output row maps to0..223; use that native row's own BG2 scroll,
map/tile snapshot, palette and priority. Material fast path uses the same fitted
BG2 sample as scalar composition. Foreground/world geometry, waterfall sprites,
actors/HUD/gameplay stay at their original coordinates. Source layer count and
native initialization/scroll remain intact. Diagnostics report native_banded_
panorama_fit. Normal224-row output and independent MD background stay unchanged.

6672 evidence: fresh practice5 opening1960 and intact earlier waterfall66108,
current settings852x503. Actual Mode1 BG1/BG2 enabled224 rows, BG3 disabled;
per-line original scroll/VRAM/palette states retained in layer-evidence.json.
Native full scene has its own initialization: descriptor+24 is not a generic
background pointer here; an exploratory decode failed and was not used. This
fit reuses the completed224-row native picture, not a decoded full512-row source
map, new plane, edge repeat or proof that SNES and MD planes correspond. Existing
MD streamed512-row/banded sampler, palettes, phase and capabilities unchanged.

6675: opening and waterfall old/new guest/nativePPU/gameplay exact. All original
line states, submitted pieces and raw BG1/BG2/BG3 dumps exact. Composed tall
background differs as intended. Native console and selected MD background
old/new pictures exact. OriginalTiming old/new/LLE exact. Actual DPI-aware
waterfall Windows client and opening screenshot reviewed: flat extensions gone,
mountain bands fill tall canvas. No full-level/FPS/all-artifact/finalTAS claim.
Broad all-level/fullMD/final unchanged original Genesis TAS goal remains OPEN.
Evidence6672 reproduction/layer states,6673 pre-edit archive,6674 renderer,
6675 focused checks,6676 qualification,6677 publication.



## Delivery6701: shared wide/tall sprite completion

Current installed-preview6695. SHA256
 df6ee09ce2bdc3da5b5da95061201f25a3ba38bbe06beb29adf87a8761c05e1b.
Only pride_final_wide.obj and native_render.obj rebuilt on6677. Native render
pacing ranges/guards unchanged; new read-only observer after original tile-cache/
uploader selection. Frozen6643 world-work budget, host/audio/resource/helpers,
assets, all502 actual launcher choices and user INIs retained. History13/444-byte
header and24-byte records remain unchanged. No generated source/submodule edits.

User requested broader visibility for all sprite types. Shared renderer now
records source-approved ordinary actor drawings before the original127-piece
rejection, covering compact/mixed and noncompact ROM pose headers with reciprocal
ownership. Original hidden/blink/fixed state is respected. Actual original
C0A6A2 post-LDA observer (logical C0A6A4; matching interpreter pre-opcode) reads
selected tile index93, B1 attributes and ACFD/ADFD conversion tables after cache/
upload selection; no CPU/RAM/VRAM/OAM/budget changes. Native submitted parts
replace provisional parts, retaining their exact tile, slot, priority and kept
status. Missing parts remain for expanded presentation, including native-centre
holes caused by extra-view budget pressure; source-sized console remains exact.
Old King-only live budget hook superseded. Existing paused giraffe, ride/vulture,
liquid/dynamic-pose and special-owner adapters remain. Newly recovered normal
parts use actual uploaded tile references. Generic direct native glyph sampling
is allowed only for immutable ROM sources; existing proven family adapters keep
their source rules. Spawn, retirement, hit boxes, AI, sound, palettes and selected
SNES/MD drawings remain independent. No scenery layer/scroll/init/edge changes.

Read [wide sprite audit](wide-sprite-visibility.md) for coverage and log semantics.
6704 acceptance binds all final sources.6696:28 isolated old/new samples for
14 practice entries x2 art styles, maximum requested1024x768; all guest/nativePPU,
gameplay and line states exact. All1806 actual prior native submissions exact.
Stampede keeps dedicated source framing; bonuses keep supported224-row framing.
Practice Hunt1 intro has no active stage by2250;6702 genuine active source3100
checkpoint supplies that missing coverage, not a claim the intro was repaired.
6699 six nearby late cases: ostrich obstacles, gorilla/coconuts, Prepared bats,
Return hyenas, Destiny boulder, final Scar retreat, all guest/native exact.
6697 repeatedly budget-omitted Destiny edge monkey0->3 parts, real pixel change.
6703 active OriginalTiming old/new/LLE guest/nativePPU exact and new compiled/
interpreted composed window exact.6698 console pixels exact and actual852x503
Windows client reviewed.6696 contact sheets and6702 active Hunt1 reviewed;
preloaded native green beetle remains exact after final source-selection fix.

Private candidates6682/6686 were NOT published. Live pose can advance beyond
captured draw pose, so raw inventory counts alone gave false partial-frame leads.
Early parallel practice cases shared an INI directory/boot file; isolated cases
supersede those comparisons. Direct raw RAM glyph sampling erased a preloaded
Hunt beetle because temporary source memory had been reused. Actual uploaded
tile selection fixes that problem; regression checked before publication.
No universal all-encounter/pixel/FPS-lock or final unchanged Genesis TAS claim.
Broad all-level/fullMD/final unchanged TAS goal remains OPEN. This delivery is
shared visibility infrastructure plus the documented actual scene samples.
Evidence6678/6681/6694 source archives,6695 final build,6696/6697/6698/6699/6702/
6703 checks,6704 acceptance,6700 qualification,6701 publication.



## Delivery6716: picture-based backgrounds without solid extensions

Current installed-preview6713. SHA256
3c82513dfde79746fb333a8466607003300c4df6fa20f11e20784f2cafa6e4f3.
Only pride_final_wide.obj rebuilt on6701. Uploaded-sprite native_render6695,
world-work budget6643 and all earlier host/audio/resource objects retained.
Same502 actual launcher choices, assets/helpers/user INIs and history13/444-byte
header retained. No submodule/generated game-code edits or new decoded assets.

User requested checking every level for solid background fallback. Remaining
solid-color extension existed in native Destiny/Prepared/Return/Pride Rock and
MD extra-height views. Remove the dominant-color extension array and its token
fill routes. Proven native Pride/King full panoramas remain; all other tall
normal-world backgrounds fit their complete selected224-row picture to the
window. Each native source row retains its own scroll/tiles/palette; MD rows
use the already verified independent MD sampler/scene recipe. This is explicit
host presentation scaling, not a newly decoded plane or proof of extra artwork.

Background also draws outside finite foreground bounds instead of world-edge
black filler; foreground/actor coordinates and source-level bounds remain.
Return keeps cached8-pixel background-row decoding for fitted rows; fixed-colour
math/palette handling and gameplay stay intact. Source-sized Stampede, bonus,
cinematic canvases and authentic flat skies, transparent/dark source areas,
actual fades/mattes remain. A naturally uniform source row is not a synthetic
single-color replacement. No new general edge-repeat/plane correspondence.
Diagnostics now say native_full_panorama_fit/native_banded_panorama_fit/
genesis_captured_background_fit or source_canvas; no dominant_edge_color claim.

Visual audit additionally found MD Exile upper blank columns. Original BG
20DDFA/3584 bytes: rows0..18 have opaque artwork only in columns0..39;40..63
are empty. Lower rows19..27 use all64 columns. Existing independently verified
08C1C8/08C26E initialization/scroll has fixed upper152 rows then8/16/24/24
scrolling bands. Reflect only the fixed authored320-pixel upper picture into
extra width; preserve canonical320 and lower full512 band sampling. Native
Exile's earlier256 reflection stays separate. No SNES/MD plane identity assumed.

6710: all10 actual main-level entries x2 art styles at max requested1024x768,
old controls reused from isolated6696; every guest/nativePPU/register/gameplay
pair exact. Current healthy states saved next to each case for future checks.
6710 binds the exact pre-MD-Exile-reflection source archived6712; final6713 differs
only by that tested conditional sampler branch.6714 confirms source-sized Return
and MD Exile pixels exact, OriginalTiming old/new/LLE guest/PPU exact, new
compiled/interpreted picture exact. Real852x503 Return and MD Exile clients
reviewed: full valley and no Exile empty columns. Return149/149 completed game
updates, observed59.65/sec excluding repeated-field final dump I/O; no FPS-lock
claim. Native6/7/8/9 and selected MD screenshots reviewed. Source sky/shadow/fade
regions remain original picture content, not newly painted replacement bands.

6707 fixture attempt was discarded: files named after.state in5858 death audit
are AFTER death, not healthy entry states; one rightly rejected for a death
source mismatch. Do not bypass that guard or claim compatibility work.6710
captures fresh actual matching entries instead.6717 acceptance binds final source,
per-scene native layer/register schedules and independent MD Exile map evidence.
No whole-level/all-camera gameplay traversal or final unchanged Genesis TAS
claim. Broad all-level/fullMD/final TAS goal remains OPEN. Presentation fallback
capabilities are not evidence of complete original source geometry.
Evidence6705/6712 archives,6706 full-picture candidate,6710 all-main audit,
6713 final renderer,6714 controls/windows,6717 acceptance,6715 qualification,
6716 publication. Current normal-world background extension uses picture data
throughout supported tall views; original fixed-framing scenes remain bounded.


## Delivery6724: smoother wide-window ostrich entry

Current installed-preview6721. SHA256
508e2736c56f8e199c20821afa5eb7e5d1f03b73815f95c680659b9dd122b14f.
Renderer-only rebuild on6716; same502 actual launcher choices/assets/helpers/
user INIs. Native sprite completion6695, world budget6643, all background
picture/Exile fixes and other frozen objects retained. History13/444-byte
header unchanged; no new fields, schema, assets, gameplay or audio changes.

User reports the second ostrich start camera looks poor. Existing preserved
6617 genuine second-entry checkpoint5813 reproduces a12-source-pixel view
jump at5847->5848: presented origin3304->3316. The old handoff deliberately
left8 pixels of the original269-pixel camera rebase uncompensated, then
linearly removed the remaining offset over512 ridden pixels. That also
started/stopped its additional pan abruptly. Absorb the entire measured
rebase and ease its removal with cubic smoothstep at both ends, using the
same completed actual ride distance. New origin3304->3305; initial first
ride1783->1784 too. Normal updates, pause and current saves retain the same
distance-based behavior; no guest camera, script, actor or collision edits.

Native foreground BG1 and separately captured native BG2 panorama retain
their own source camera/phase offsets, sharing only the handoff weight.
MD scenery keeps its independent original sampler at the projected camera.
No new layers, repeats, hidden artwork or plane correspondence claimed.
6722/source-raster-evidence.json retains per-row source registers at pre-entry,
entry and mid-pan; all earlier per-scene background limits still apply.

Focused6722 first/second entry old/new guest/nativePPU/gameplay exact. Before
entry and after512 ridden pixels second-ride pictures exact. Both256/320
original-sized console pictures exact; OriginalTiming compiled/LLE picture,
guest/nativePPU exact. Current mid-pan save resumes with exact image/state.
MD background choice checked independently; two actual paced Windows captures
VIEWED, including second ride in progress. An initial console test correctly
rejected a full save after a resource-choice change; controls use its intact
native backend in both binaries instead, no guard bypass/migration. Successful
samples reused while completing controls. No full-game/TAS/FPS-lock claim.

Previous6718 normal-mode verification:56 checkpoint combinations (14 entries,
two artwork presets,256/320 requested widths,224 rows) match6695 exactly in
picture/guest/nativePPU/gameplay; paced Return movement matches and actual
normal960x672 Windows client reviewed. This was targeted checkpoint coverage,
not a full walkthrough. Final unchanged original Genesis TAS remains OPEN.
Evidence6719 observation,6720 exact baseline,6721 candidate,6722 checks,
6723 qualification,6724 publication. Launch existing preset CMD after reopening.



## Delivery6755: rendering reuse with identical source pixels

Current installed-preview6753. SHA256
72ec3912d78f3557da5d4098c750af3973aef7f08ebc3fb8719a67910820eb71.
Renderer-only rebuild on6724, same502 actual launcher choices/assets/helpers/
user INIs. Native sprite completion6695 and work budget6643 remain frozen;
history13/444-byte header unchanged. No guest/gameplay/audio/camera/timing,
counter, save-schema or new asset changes.

Large user window2560x1511 (internal852x503) had substantial host-rendering
cost in Graveyard, Exile, Hakuna, Destiny and Prepared. Ordinary native8px BG2
and fitted foreground rows now decode in tile runs. Existing native material
correspondence is cached for one draw, bounded64 probes with original sampler
on cache miss. Existing transparent source-backdrop results reused under the
same window/math/BG3 guards. Foreground beyond finite native map bounds still
uses the existing reflection/clamp; reflected tile rows now decode in runs
too. No new layer/scroll/initialization, hidden art, repeats or capability
claim. Native and MD scene recipes remain independent. Preserve Exile upper
256 reflection and Graveyard/Exile source223->222 band join exactly.

Focused user-size median rendering intervals old->new: Graveyard17.38->10.19ms,
Exile15.13->7.60, Hakuna12.97->7.92, Destiny14.44->9.55,
Prepared12.95->7.83, Return8.79->8.05, PrideRock15.39->8.26.
Genuine waterfall first100 fields35.56->7.32ms. Later tall camera position
previously remained about45 updates/sec after initial optimization; final
reflected-run fix gives58.32 in a clean paced sample,210/210 guest draws.
Other ordinary entry samples about59.5-60.1; all4 active bonuses about60.
Stampede202/210 fresh fields matches old public build exactly: existing
guest draw cadence, not host capacity. Occasional host spikes remain; no
every-camera/full-route60-lock guarantee.

6731 baseline original polled sweep covers main0-7 and bonuses but exhausts
the53099-word controller in Prepared;6738 independent Return/finalScar/blue
suffix also exhausts before credits. These are NOT a current full TAS pass.
Post-fix use actual scene-validated healthy entries for all10 main levels,
all4 bonus types and genuine late waterfall/Return/ostrich snapshots. Separate
6748 original ending suffix reaches credits62500: active blue has just one
31-field outgoing scripted hold. No ending program edits. Final unchanged
original Genesis TAS from title through ending remains OPEN.

6734 exact controls:27 cases, all10 native/MD-art main entries at maximum
1024x768 plus7 affected native original-size scenes. Presented pictures,
guest/nativePPU/register lines/gameplay exact. Old/new late controls and
OriginalTiming compiled/LLE exact. Final real paced waterfall Windows client
capture VIEWED. Screenshot capture overhead measured separately from clean
paced samples; keep first CSV row per field to exclude duplicate final PNG
dump cost. Initial scene-labelled saves2/5/6/7 were outgoing bonus programs,
not main entries; replace with actual descriptor-validated6710 snapshots.
Initial Pumbaa1846 sample entered result fadeC53E5E; final1700 entry stays
activeC53B1F. Preserve failed probes; do not count result holds as gameplay
drops. Initial per-pixel equivalence failures caught a missing existing band
join and were fixed before publishing. No native/gameplay fallback changed.

Evidence6731/6738 baseline sweeps,6734 exact/performance controls,
6748 ending,6756 bonus/early entries,6757 Stampede cadence,
6754 qualification,6755 publication. Reopen the existing preset CMD;
add -FpsCounter for UPDATES/FPS. No new recordings or user-save changes.


## Delivery6765: secondary factory fountain

Current installed-preview6763. Only pride_final_wide.obj rebuilt on6755;
all large-window performance work, native6695/world budget6643 and other
gameplay/audio/assets/helpers/settings retained.502 launcher choices unchanged.

New copied slot2 field26738 is Graveyard, player3957/146 and source camera
3308/37; paused852x503. FactoryB713/C58D44 actionC2D1D3 has live primary
DD45 and secondaryDC57 at actor+28,48 world pixels apart, same generated
7EAB06 frame/attributes and live height513 through base736. Only primary
pieces were captured after native draw capacity was exhausted. The generic
static ROM sprite completion intentionally excludes generated WRAM drawings.

After existing source tail completion, recover only missing secondary pieces
outside the original console rectangle. Require reciprocal factory ownership,
same current generated pose, identical primary/secondary attributes and no
hidden/flip flags. Copy primary's actual tiles/phase and exact actor offsets,
never duplicate local pieces; use unused host slot127. Preserve all previous
pieces in exact order. Both columns retain existing live-base clipping and
independent native/MD artwork handling. No new background recipe, layer,
scroll, initialization, edge fill or synthetic water pool; no guest/OAM/VRAM/
hazard/gameplay/budget/save changes. Normal original-sized picture exact.

6764 current full paused old/new guest/nativePPU/gameplay hashes exact;
66 secondary source pieces restored with exact48px screen offset and matching
local source/tile attributes. Existing pieces exact prefix, no duplicates.
Earlier actual124226 liquid checkpoint retains guest/gameplay; independent MD
artwork checked via intact native backend. Real Windows852x503 client VIEWED
with both fountains visible. Initial candidate inserted extra parts before
existing tails; exact-prefix check rejected it and final appends after tails.
Save preserved under6758; short6759 ordinary replay revealed imminent death,
not a traversal acceptance. No full-game/performance/TAS claim for this fix.

User also reports a hole beneath water. Exact gap not yet identified; optional
clarification pending whether directly beneath column or other scenery below.
Do NOT mark that separate report fixed based only on the restored fountain.
Earlier 6664 tail repair and current performance work preserved.

Evidence6758 user save,6759 local motion,6761 taller inspection,
6762 pre-edit archive,6763 candidate,6764 checks,6765 publication.
Reopen Play SNES Visuals with Genesis Gameplay.cmd and load slot2.


## Delivery6778: waterfall platform presentation

Current installed-preview6776. Renderer wrapper only on6774; same502 actual
launcher choices, assets/helpers/settings and all earlier fixes retained.
No generated/C4 guest-unit/framework edits, audio, resource tree, native budget
or save-schema changes. Original native and Genesis log controllers both use
cameraY-40..Y+260 with300px wraps (6779 cartridge operands/disassembly).

User clarifies gaps where waterfall logs should be. Earlier6551 adaptation
lengthened the same actor set's loop by tall margins:579px at852x503. This
changed spacing/return timing. Restore original operands at all four existing
C4 callbacks; keep them as optional read-only300px diagnostics. Native motion,
collision, real actor count, generator creation, reset choice and wrap side
effects now retain their original300px cycle at any window height.

For the extra tall presentation only, unfold adjacent turns of each currently
owned original waterfall-log drawing at300px intervals. Validate reciprocal
actor/draw/pose and activeC58AEC/C48DF7; only unfold after the real actor is in
its original canonical window. Follow source X reset at actor+2E and alternating
horizontal facing on each turn. Limit to the finite0..1080 waterfall; skip
retired/x-zero, hidden/fixed, initializing and stale ownership. All extra parts
are outside native224 canvas; they converge on the real source drawing at its
original wrap, before Simba can reach them within the gameplay camera. No
additional actor/collision surface or guessed background extension is created.
MD complete-art drawing groups by object plus turn origin, retaining full MD
artwork rather than losing additional turns to its object deduplication.

This supersedes6551's longer physical loop and its "no presentation replicas"
approach. Adjacent-turn presentation follows the proven original period/facing
and never changes the platforms underneath the player. Background plane/layer/
scroll/init/edge/capability recipes remain unchanged. Original finite generator
availability remains in charge; no guarantee that every waterfall region must
always contain a platform regardless of its original script state.

6777 preserved6465 waterfall66106, ordinary Start release and480-field replay:
old579 versus new300, original endpoints both1915/413 HP2/five spares;
native pieces6->22 with adjacent turns, all300px apart, correct facing parity,
outside the original224-row picture. Short-height852x224 and console old/new
whole guest/PPU/picture exact. Short/console fixture ends after an imminent
death; NOT a waterfall traversal or cross-height gameplay-equality claim.
An initial cross-height log-trace comparison failed because different view
activation produces different gameplay/death; not counted as equality evidence.
Tall original-timing compiled/LLE whole guest/PPU/picture exact. Native and MD
art reviewed; actual paced Windows client VIEWED with uninterrupted extended
stream. Existing short/console checks reused after harness correction.

Legacy full6465 envelope is rejected by current ownership guard; all controls
use its intact native backend consistently, no migration/guard bypass. No user
saves changed. Old stretched-period states settle back into the original cycle
on ordinary updates. No full traversal/TAS/FPS-lock claim. Overall original
Genesis TAS goal and unidentified Graveyard hole beneath water remain OPEN.
Evidence6775 pre-edit,6776 candidate,6777 controls,6779 both original programs,
6778 publication. Reopen the existing preset launcher.


## Delivery6852: Prepared partial blank presentation evidence

Current installed-preview6847. SHA256
a6e497be46994cd1fb3d43093feb04615afe78d55356cca59345a01122766ae2.
Wide wrapper plus native C5part19 clone on6822; same502 actual source choices,
assets/helpers/INIs/user saves. No framework submodule, ROM opcode, audio,
gameplay/collision rule, actor-count/lifetime, camera or save-schema change.

NEW user slot2 preserved6830: Prepared119016,4HP/nine spares, Simba3149/596,
852x503. Panther hits leave3HP119102,2HP119314,1HP119481. Raster6831 catches
isolated forced blanks119484/119492 (one row),119556 (eleven rows), still
1HP/alive. Last field has728 entirely black physical window rows out1511.
These hit flashes precede death and are not caused by corpse centering.
WorldPresentationLine's existing tall-view partial-blank policy now also
covers initialized Prepared C004E5. Only isolated forced blank rows borrow
nearest completed world metadata; ordinary dark rows and fully dark fades
remain. Original224-row views unchanged. Per-scene evidence: Mode1/BG1+BG2+
OBJ main19/sub0, bgsc65/73/72/0, bgchr0, valid line12 scroll195/191 and342/0,
brightness15, math48/0/0. Existing initialization/streaming/VRAM/palette,
layer count, scroll, authored panorama fit and edge recipes unchanged.

User's death-centering suspicion ALSO exposes a separate visible defect.
Actual health death119648 reaches corpse age0 at119653: stored world offset
234/Y148 puts it outside the fixed380x224 death canvas. In expanded regular
world views, map the displayed world anchor to the224-line death canvas:
horizontal offset=(displayedX-viewWidth/2)*224/viewHeight;
Y=(nativeY+nativeRow)*224/viewHeight. Here origin becomes-14/Y168. Same MD
approach/poses/timing/palette choices, no clamping, gameplay movement or
invented frame. Capture while world is live, before the renderer switches
canvas. Shared normal cub/adult lifecycle benefits; no claim for Pride's
separate lifecycle or unsupported fixed scenes. Original-sized mapping stays.

Retain6825's safe contact tail traversal, now as a native C loop rather than
forwarding the whole hot search to the CPU interpreter. Two compiled source
call sites invoke the SAME bounded tail-step helper then jump to original
next-node blocks, skipping the same JSL/prologue/dead local stores as LLE.
Original native body/source files stay unchanged; maintained6836 builder
generates an ignored clone. No native CPU stack/arena recursion growth.
Slot3 freeze control has complete6824-new guest/PPU equality; exact original
hit encounter old/new guest/PPU equality; OriginalTiming compiled/LLE equality.
No broad performance or full-game60fps claim.

6840 hit field119556 old/new whole guest/PPU/gameplay identical, black rows
728->3 (ordinary outer fit), healthy picture exact. Final6848 death maps source
anchor into view, visible at age0 and72, same guest/PPU; actual death->respawn
ends4688/528,6HP/eight spares, whole guest identical to earlier path. Normal-view
119653 control is still1HP due different activation/camera: it proves unchanged
normal presentation/guest, NOT a normal-view death traversal. OriginalTiming
compiled/LLE death picture/guest equal. Reuse all valid focused checks; no TAS.

Real Windows6850 final hit and early corpse captures VIEWED. Private present
hold pumps Windows messages; private hold/renamed counter objects NOT shipped.
Earlier destroy/present holds6840/6842 blocked PrintWindow and captured black
on both builds: INVALID presentation evidence, replaced by6844/6850. First
short pre-flash restored checkpoint6837/6838 shifted raster phase and did not
reproduce the flash; actual-source uninterrupted replay used instead, no save
timing/migration change. Initial corpse anatomical-bbox-center assertion was
wrong for source art's anchor and removed; retain original MD target/offsets.

Reopen existing preset launcher and load current slot2. Earlier Hakuna damaged
VRAM save6817/6829 is a DIFFERENT preserved slot2, still OPEN (no pre-death save).
Separate all-level/full-MD/final unchanged original-Genesis-TAS goals stay OPEN.


## Delivery6876: no background recipe changes in death audit

Checked natural death/respawn in all10 main levels and separately both ostrich rides at the user's2560x1511 window (852x503 world), SNES visuals/Genesis gameplay and sound. Stampede retains its fixed special canvas. King ordinary case is its water/hazard path; other main-level routes exercise cub/adult bodies. All12 consume one spare life and return with positive health. Real Windows6870 body captures for all12 VIEWED, plus sequence samples for movement/late corpse/respawn. Not every hazard/final-life/source combination, not a full walkthrough/TAS or universal performance claim.

Fixed3 concrete paths: Pride's independently owned corpse used native world offsets on the fixed death canvas and could start beyond the right edge. The live expanded view now maps its origin into the224-line death canvas, retaining original MD approach/poses/target and source-independent SNES art/colors. Original-sized placement remains. Ledge and ostrich blocking deaths retain their outer actor action while running exact shared death child C0E0A8; requiring outer C30792 missed them. The shared owner/child recognition now accepts that verified child even with a ledge/rider action; caller guards still require matching scene/age, defeated player, lives and non-skipped display. This fixes the native reflected/stationary picture and stale lives HUD in Hakuna and both rides, and restores the selected health-death music. King was excluded from the death-music scene set; add it with the same inherited shared death cue. Water/lava splash identity remains distinct.

Focused6874: healthy Prepared, healthy King and original-sized Pride old/new whole guest/PPU/picture equal. Four affected death checkpoints have complete compiled/LLE OriginalTiming guest/PPU/picture equality; each starts selected MD430 exactly once in the sampled interval. Four corrected full cycles6865 return at the same fields and life counts as baseline. All other routes reused from current-build audit6854; Destiny's successful large-window encounter loop and a separate normal-size death cycle6873 both pass. Initial idle/left/paused fixture attempts that did not die are NOT passes; first ride required ordinary Start to unpause its saved scene. No HP/actor/RNG writes. Private observer attempted in-render snapshots but those are not usable; host-loop6870 before-death saves supply the actual valid gate checkpoints. Only sparse PNGs/logs/checkpoints retained, no full recordings.

No framework submodule, ROM/opcode, guest movement/collision, camera, background recipe, asset payload or save format changes. Existing6825/6852 contact safety and hit-flash fixes retained. Earlier saved-corrupt Hakuna VRAM6817/6829 remains separate and OPEN; these fixes do not repair that saved graphics payload. Separate all-level/full-MD/unchanged-original-Genesis-TAS goal remains OPEN. Reopen Play SNES Visuals with Genesis Gameplay.cmd for this delivery.

## Delivery6898: viewport startup guard; backgrounds unchanged

Current6898 /installed-preview6889 fixes the reported original-sized Full Genesis TAS getting stuck in Be Prepared. Binary11356c436ae87e4993967fbbea4e5553738fe5e4a29758cbecc83ff087f11e43. Wide wrapper rebuild only on6876; same502 actual source choices/assets/helpers/INIs/saves retained. No native game opcode/generated body, framework, camera rule, audio, save format or background recipe change.

The adult loader guard intended to defer EXTRA large-view activation also blocked the ordinary selected Genesis320x224 initial scan. Failing current6876 cold replay6878 skips rock384/64 and constructs608/80 first after stage initialization. Original Genesis6886 constructs384/64 before the ordinary stage RNG initialization, then608/80 afterward; both legitimately seeaa0b4c. Wrong order shifts later randomness: rock3472/144 waits31 rather than original58 and hits Simba at canonical poll39371.6880 captures its actual C58780/C06F5B attacker/position/packet. Input continues, but repeated deaths leave the baseline inlevel7 at54000. Local OriginalTiming also fails; no timer/seed/input retuning is justified.

LiveSpawnViewport now allows adult initialization when activation fits the selected ORIGINAL scene width and224-line canvas. Readiness still guards optional extra width/height. No special TAS/coordinate condition, invented actor or rescan, new toggle or RNG write.6895 read-only calls prove384/64 then608/80, eachaa0b4c around the existing reset, matching original6886. Corrected route matches original positions/health at the former hit, later1UP, intentional lava retry and Return entry (6897 local-evidence).

6891 resumes the exact current40000 checkpoint with unchanged16883-word suffix through Prepared, Return, Scar and credits65000,10HP/eight lives.6893 independently repeats FROM TITLE on the corrected graph: all53099 words (1109 existing menu adaptation plus51990 unchanged original gameplay words), all ten main levels and credits65000,10HP/eight lives. No load/debug/practice, invulnerability or HP/actor/RNG/input edits in that cold run. Current ORIGINAL-SIZED Full Genesis ending TAS gate PASSES. Large-window TAS compatibility, every source combination/asset and all other reports remain outside this claim. Broad all28/source-coverage goal stays OPEN.

6892 exact old/new controls: fresh852x503 Destiny and Prepared, plus256x224 Prepared; whole guest/nativePPU/gameplay and picture identical.6896 corrected nearby Prepared OriginalTiming compiled/LLE whole guest/PPU/picture equality. Real Windows6894 Full Genesis replay with sound/FPS VIEWED passing the problem and entering Return. No full video; bounded logs/sparse captures/checkpoints only. Original reference6882/6886 uses the existing movie/genuine states without memory edits. Historical5550 local fixture already contains the documented bad retry path and is NOT acceptance; current cold-run checkpoint supplies valid investigation.

Visible playback resumed from corrected43000 before the problem. Reopen ordinary launcher for the installed fix. Previously diverged saves cannot recover the consumed actor/random history; restart the level or replay from before entry. Earlier saved-corrupt Hakuna VRAM6817/6829 remains separate and OPEN.

## Delivery6960: fountain bottom strip in tall view

Current6960 /installed-preview6958 fills the exposed strip directly below the two Graveyard green waterfalls in the user's current slot2. Copied6956 original field25719: paused852x503 view, camera3308/436, origin265, Simba4023/521, factoryB713/C58D44 with primaryDD89 and secondaryDD9A. Original top659, live height77 and base736; map has48 rows/768px. The taller picture exposes the remaining32px below the source base. User explicitly confirmed this bottom-right black space. Original C2D35A computes top=base-height; earlier6664 restored tails only through that base. Original native6659/MD6658 pool references demonstrate the authored streams, not artwork beyond base736.

This is a bounded tall-view presentation adaptation: for a reciprocally owned Graveyard fountain with an available body and base exactly32px above the finite map bottom, continue its actual current body rows through those32px. Original32px alternation is preferred; a short retracting column can reuse its available live body row, never a stale phase or head-only cap. Both factory draws retain their current colours, phase, width,48px spacing and source choice. Last partial row clips at the map edge. Independent MD whole-column rendering uses the same presentation height. No horizontal pool, new background plane, new scroll/init/repeat recipe, decoded asset or enlarged liquid collision. Source base, actor height, hazard, palette, upload, OAM and gameplay remain unchanged. Original224-row viewport does not extend the fountain. Fully retracted/head-only spouts retain their original presentation.

Focused6959 saved paused old/new120 fields preserve entire WRAM/native picture; original320x224 window is exact. All original current pieces remain an exact prefix, with eight body parts appended at local80/96 for the two owned draws. Natural Start-unpause120 fields preserve full guest/native frame; that existing route falls to death, not a traversal acceptance. Independent MD art from the intact native payload also preserves guest/native picture. Actual paced Windows saved-view capture and both artwork previews reviewed; changes confined beneath the two streams. No unrelated full walkthrough. Only pride_final_wide.obj changes on6955; prior vulture, preset/browser and performance work retained. Original slot/settings/presets/assets preserved. Broad all28/source-coverage goal remains OPEN.


Audit7126 qualification: the inherited first/second ostrich-death tapes finish in the normal King giraffe section with this delivery, so7125 qualifies those endpoints only and does not certify active ostrich gameplay/transitions. Fresh Stampede remains a fixed source canvas by design; normal and expanded-window presentation are checked without claiming a new wide Mode7 renderer. Initial loading/death/blank samples from7118 are not accepted as healthy level coverage. Fresh7124 samples replace Graveyard/Stampede/Bug Toss. No claim of universal bug absence, a new full walkthrough, or fresh TAS completion.
