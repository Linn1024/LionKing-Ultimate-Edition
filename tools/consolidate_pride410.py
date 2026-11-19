"""Consolidate current project facts, preserve history, and bind route evidence."""
import json,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

handoff='''# Lion King PC development handoff

Current410, 2026-11-10. The first-level fidelity goal remains OPEN. Public398 is
the current Windows player; no game/runtime change was made in404..410.

- Player: `dist/installed-preview398/LionKing.exe`
- SHA256: `be29819ad0891814b99350e755f4c608c7b8536c465aa9531d8fc12876d90b74`
- Launcher: `scripts/RunInstalledPreview.ps1`, used by the existing root Play CMDs.
- Default data: `game-data/install.json`, scene-v2 and sprite-v2 required.
- Settings and earlier assets/builds remain preserved.

Read [current first-level status](pride-lands-status.md) for requirements and
actual limits. The previous long handoff and status are preserved in full at
[handoff history](history/handoff-through403.md) and
[status history](history/pride-status-through403.md). These are historical;
do not treat an old unfinished item as a current bug without checking later work.

## User priorities

Build the playable game through the ending. Match what an experienced player
sees, hears and feels; CPU/assembler equality is a diagnostic aid. Do not pursue
one-frame transitions, instrument-only differences or old development-save
compatibility. Run focused checks for changed behavior, with bounded captures.
Do not repeat native75/All Bugs after local UI/art/data changes without cause.
Hybrid emulation is allowed where practical. Installer-prepared resources remain
the intended playback path. No agents unless explicitly requested.

## Recent shipped work

| Work | Scope and evidence |
|---|---|
| Available MD preset398 | Resources MD/F7 (SDL), Available MD (ImGui). Draft only; supported ready leaves inherit MD, unavailable leaves explicitly SNES. Branch/leaf overrides and Apply/restart preserved. [Details](available-md-preset.md);401 actual SDL interaction,402 publication. |
| Prepared gameplay390 | Sprite-v2 contains default starts, lizard flags,836 pose hitboxes and14 roar tokens/delay. Installed activation replaces their ROM initialization, artwork/palettes/policy unchanged. [Details](pride-prepared-gameplay.md);391 direct/Setup,392 route,395 publication. |
| Prepared terrain382 | Scene-v2 contains8000 first-level contact cells and immutable second-level palettes. [Details](pride-prepared-contact.md);380 direct/Setup,381 route,384 scoped qualification,385 publication. |
| Second-level scenery372/362 | MD foreground12391/12400 cells,9 native cells; three-region Plane-B scroll, camera wraps and palette fade. [Foreground](cant-wait-prepared-foreground.md), [background](cant-wait-live-background.md). Other layers/actors/gameplay are not fully MD. |
| Hyena HUD356 | Identical544-byte OAM reuploads retain sprite ownership when no new draw list exists. Fixes reported wide/narrow HUD flicker. [Details](pride-hyena-hud-flicker.md). |
| Captions349/268 | Level titles horizontally centered; multi-line titles center each line. Independent Pride caption sources remain. [Details](level-caption-centering.md). |
| Audio319/327 | MD battle cue belongs to opening jump; porcupine sound uses counter28 independently of contact source. [Hyena](pride-hyena-entrance.md), [porcupine](pride-porcupine-voice-timing.md). |

## Current walkthrough evidence404..408

The exact Available MD draft captured by401 now completes an ordinary power-on
Easy route to main level1 with all8 spare lives. This includes all currently
available MD leaves, not just the older hand-authored subset.

404 initially used a recording with a native-menu prefix.405 shows it selected
Difficult under MD navigation.406 substitutes the already verified737-poll MD
menu prefix and retains the entire previous gameplay suffix after poll638.
Easy is actually observed at entry906. No game/ROM edits, source reduction,
practice macro or loaded state is used. Credited input remains ignored under build/.

407 repeats the full route in a real window, with matching sampled guest state,
final picture and whole PCM. Its4400 screenshot is a legitimate next-level black
loading interval, not a boss view; exclude that capture from visible arena proof.
408 captures inside actual level0/arenaC0080D, with descriptor/health/field guards;
the real nonblack arena client was inspected. Do not change game timing to repair
a recording's menu inputs or a verifier's badly chosen screenshot field.

## Remaining first-level work

The goal is not yet certified as complete. Broader original MD enemy/action,
interruption, rare effect/voice and fall-death fidelity remains scoped or
unqualified. Generic unsupported nodes explicitly use SNES; do not advertise
full MD behavior because a route completes. Installed tables/images are prepared,
but the whole hybrid runtime still consumes original ROM data.

The concrete remaining current-combination gate is a basic save/retry continuation
with the full Available MD profile. Earlier current-format save/menu/audio checks
exist, but404..408 do not qualify that combination. Use one same-build ordinary
checkpoint and correctly sliced remaining polled input, not an old-save matrix.
The earlier383 mismatch restarted its full tape at poll0 after loading3750; it
is not evidence of a game/save defect. Player-visible feedback was requested
asynchronously; it is optional and no answer is assumed.

## Subsystem reading map

- Background/layer/scroll/initialization rules: [background audit](background-audit.md).
- Resource model/preset: [available MD](available-md-preset.md),
  [parent inheritance](resource-tree-inheritance.md), runner/tlk_resources.*.
- Prepared data: [gameplay](pride-prepared-gameplay.md),
  [contacts](pride-prepared-contact.md), scripts/Setup.ps1, engine/cmake/Tlk*Assets.cmake.
- Gameplay status: [first level](pride-lands-status.md),
  [reference](pride-lands-reference.md), engine/runner/pride/ and native adapters.
- Final-life/menu/current saves: [runtime checks](pride-menu-current-checks.md).
- Audio ownership: [music output](pride-music-output.md),
  [bounce lifetime](pride-bounce-driver-lifecycle.md), runner/tlk_*audio*.
- Later stages: [next-level status](next-levels-status.md), scene-specific documents.
- Build details: engine/AGENTS.md, engine/docs/HOW_IT_WORKS.md and VERIFYING.md.

## Working rules and evidence

Preserve local changes; never edit snesrecomp or recomp-ui submodules. Generated
game code, ROMs, extracted resources and recordings stay ignored. Native source
adapters/data codecs belong in maintained code, with honest capability guards.
Verify relevant presentation with an actual window as well as guest-state data.

`tools/pride_arena_history.py::bound` validates current or registered archived
source hashes and relative artifact hashes. Archive any bound source before
changing it, register the archive, and retain failed reports with their scope.
Latest source archive409 preserves the former handoff/status; current aggregate
is `build/pride410-audit/report.json`. All404..408 runs are terminal.

The old1.55-second figure concerned title loading, not a proven hyena defect.
Installed title-bank work already reduced it. One-frame title experiment338
was never published and was restored by339; do not resume it by default.

After this first-level goal is actually complete, create the explicitly requested
next goal for every remaining level through the ending. Do not create it early
or mark the current goal complete because only its routes pass.
'''

status='''# First-level completion status

Current410, 2026-11-10. Public398 is playable through Pride Lands with supported
independent SNES/MD choices. The broader first-level fidelity goal remains OPEN.
Read [handoff](HANDOFF.md) for the current player, priorities and subsystem map.
The full previous chronology is retained in [history](history/pride-status-through403.md).

## Current evidence and remaining scope

| Requirement | Evidence | Assessment |
|---|---|---|
| Windows installed player |402 installed candidate/publication;401 real UI and408 actual arena window | Usable published398; existing data/settings preserved. |
| First-level walkthrough |406 exact Available MD preset, ordinary Easy power-on route;407 real-window replay, next level with all8 spare lives | Proven for this route/preset. The earlier native/source-subset routes remain separate evidence. |
| Source tree and switching |401 preset draft, explicit native unavailable leaves, branch inheritance, contrary leaf override, saved Apply and playable restart | Proven SDL flow; ImGui button compiles and uses the same model, without separate GL interaction proof. |
| Width/HUD/title presentation |356 fixes reported hyena HUD ownership flicker;349 centers multi-line openings;408 current320 arena client inspected | Known reported defects addressed. No new layer or timing claim from a screenshot. |
| First-level scenery | Prepared scene-v2:8000/8000 paired foreground cells; original Plane-B recipe and lifecycle evidence in background audit | Full prepared cell coverage; decoded assets alone are not renderer proof. Preserve layer/scroll/edge guards. |
| Prepared resources |391 original/installed836 hitboxes, starts, flags,14 roar tokens;380 contact cells/palette tables; actual Setup and default publication395/385 | These resources load from packages. Other original/hybrid runtime data remains; whole-ROM independence is unclaimed. |
| Audio independence and playable mix |392 before/after table migration preserves gameplay/client/PCM;406/407 full preset route and PCM parity; earlier ownership/music/event evidence linked below | Supported cues work on the exercised paths. Do not claim every original effect or unobserved sound-owner context. |
| Basic saves/retries | Earlier current-format menu/audio/gameplay evidence exists; full Available MD state written at6000 in406 | Full preset current-combination cold save/retry still unqualified. No old development-save compatibility requirement. |
| Original MD first-level fidelity beyond exercised actions | Shared-rule/original comparisons and scoped adapters in subsystem docs | Broader enemy/action/interrupt/rare-effect/voice/fall contexts remain unqualified; do not infer complete equivalence from successful routes. |

No new gameplay fix was needed in404..410. The old recording initially selected
Difficult because MD title navigation changes sampling.406 uses the existing
verified MD-menu input prefix to select Easy and preserves its complete gameplay
suffix. The resulting full preset route reaches level1 with8 spare lives.

407's real-window4400 capture is black during the legitimate next-level load.
Its complete-route guest/client/PCM checks remain valid, but that PNG is not
visible boss evidence.408 captures a nonblack arena view under actual scene
guards. Do not pursue a one-frame transition correction for this.

## Existing baseline/release gates

The archived238 observer was restored and qualified by245. Its report passes13:
neutral3000-field picture/WRAM/PCM pilot, both60648 tracked All Bugs histories,
original endpoints and execution-mode agreement. The current objective's old
"qualify archived observer" item is closed. These are inherited226 baseline
gates, not newly run398 tests. Native75237 likewise reports302/302 endpoints.

The menu continuation/source/timing/pixel gates were completed or qualified by
246..265. See [the current checks](pride-menu-current-checks.md), including the
explicitly corrected old harness assumptions. Later edits retained the native
game-program objects, with focused source/data/renderer checks recorded at each
change. Do not repeat full unrelated matrices after a local edit.

## Practical next work

1. Qualify one ordinary current-build save/retry with the full Available MD
   profile. Keep recorded polled-input bookkeeping correct;383's poll0 restart
   after loading3750 does not prove a save bug.
2. Investigate a naturally visible remaining first-level difference when one is
   identified. The unsupported generic movement/combat/enemy nodes are explicit
   native choices; exact original MD behavior beyond the scoped adapters is not
   certified. Do not invent corrections or widen capabilities without evidence.
3. Keep whole-level original fidelity, basic usable lifecycle, and accurate
   resource coverage distinct. First-level completion still needs the remaining
   requirements satisfied; a passing route alone cannot close the goal.

## Useful subsystem documents

- [Background layers and recipes](background-audit.md),
  [first-level background lifecycle](pride-background-lifecycle.md).
- [Original reference](pride-lands-reference.md),
  [current contact/rolling coverage](pride-contact-current.md),
  [wall response](pride-wall-response.md), [ledge physics](pride-ledge-physics.md).
- [Porcupine applicability](pride-porcupine-applicability.md),
  [difficulty](pride-porcupine-difficulty.md),
  [walking roar](pride-porcupine-walking-live.md),
  [hyena recovery](pride-hyena-recovery.md),
  [hyena entrance](pride-hyena-entrance.md).
- [Procedural/static effect classification](pride-effect-coverage.md),
  [pickup flight](pride-pickup-flight-art.md), [sparkle](pride-popup-art.md).
- [Music output](pride-music-output.md),
  [bounce ownership lifetime](pride-bounce-driver-lifecycle.md),
  [menu/audio/saves](pride-menu-current-checks.md).
- [Prepared gameplay](pride-prepared-gameplay.md),
  [prepared contacts](pride-prepared-contact.md),
  [available-source preset](available-md-preset.md).

These older subsystem documents retain their dated scopes. Use the current
handoff, latest retained reports and actual source before treating old open
items as unfinished implementation. Full historical status remains available;
no evidence was discarded during consolidation.
'''

(ROOT/'docs/HANDOFF.md').write_text(handoff,encoding='utf-8')
(ROOT/'docs/pride-lands-status.md').write_text(status,encoding='utf-8')
devlog=ROOT/'engine/docs/devlog.md';text=devlog.read_text(encoding='utf-8')
text+='\n\n## Full Available MD walkthrough404..410\n\nExact401 preset completes ordinary Easy power-on Pride with8 spare lives and\nreaches level1 (406/407). Old native-menu prefix404 selected Difficult;405\nobserves that menu outcome.406 uses the existing737-poll MD-menu prefix and\nretains the entire gameplay suffix, without game edits/source reduction.407\nfull guest/client/PCM replay checks pass, but its4400 PNG is a legitimate black\nnext-level load, not boss proof.408 actual scene-guarded Windows arena view\ninspected. No timing correction or unrelated suites.409 preserves full handoff/\nstatus text in archives and docs/history;410 consolidates current requirements\nand evidence. Basic full-preset current save/retry and broader original action/\neffect fidelity stay unqualified. First-level goal remains OPEN.\n'
devlog.write_text(text,encoding='utf-8')

reports=[ROOT/name for name in ('build/pride404-preset-route/report.json','build/pride405-start/report.json','build/pride406-preset-route/report.json','build/pride407-preset-window/report.json','build/pride408-boss-window/report.json','build/pride403-bindings/report.json')]
for p in reports:bound(p)
manifest=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'))
cache=(ROOT/'game-data'/manifest['scene_cache']['file']).read_bytes();scene=struct.unpack_from('<12I',cache,120)
assert scene[11]==8000 and scene[9]//2==8000
native=ROOT/'build/pride-menu245-allbugs/report.json';n=json.loads(native.read_text());assert n['result']=='PASS' and len(n['checks'])==13 and all(n['checks'].values())
paths=[Path(__file__),*reports,native,*[ROOT/name for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/history/handoff-through403.md','docs/history/pride-status-through403.md','engine/docs/devlog.md','game-data/install.json','scripts/RunInstalledPreview.ps1')]]
out=ROOT/'build/pride410-audit';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='PROGRESS_GOAL_OPEN',previous_goal_turn='progress',full_first_level_complete=False,walkthrough=dict(preset='Exact Available MD401 draft',difficulty='Easy selected through ordinary Options',next_main_level=1,spare_lives_retained=8,real_window='408 scene-guarded arena;407 black transition PNG excluded'),foreground_cells=dict(prepared=scene[11],total=scene[9]//2),closed_old_requirements=['245 archived observer qualification; inherited report inspected, not rerun','246..265 menu/source/release gates remain historical qualified evidence'],remaining=['One basic full-preset current save/retry continuation','Broader original MD enemy/action/interrupt/rare-effect/voice/fall fidelity unqualified; no speculative/instrument-only fixes'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('Consolidated current handoff/status; full history retained. Full preset completes Pride with8 spare lives; goal stays open.')
