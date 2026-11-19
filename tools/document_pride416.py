"""Close basic current save/retry evidence while preserving full goal scope."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reports=[ROOT/'build/pride411-save/report.json',ROOT/'build/pride414-retry/report.json']
for p in reports:assert bound(p)['result']=='PASS'
path=ROOT/'docs/HANDOFF.md';text=path.read_text(encoding='utf-8').replace('Current410,','Current416,',1).replace('no game/runtime change was made in404..410.','no game/runtime change was made in404..416.',1)
old='''The concrete remaining current-combination gate is a basic save/retry continuation
with the full Available MD profile. Earlier current-format save/menu/audio checks
exist, but404..408 do not qualify that combination. Use one same-build ordinary
checkpoint and correctly sliced remaining polled input, not an old-save matrix.
The earlier383 mismatch restarted its full tape at poll0 after loading3750; it
is not evidence of a game/save defect. Player-visible feedback was requested
asynchronously; it is optional and no answer is assumed.'''
new='''The basic current-combination save/retry gate is CLOSED by411/414; read
[current save/retry](pride-current-save-retry.md). A current published/default-data
arena save resumes with correctly sliced polled input, exact endpoint picture/
guest samples/PCM and a completed first level. A separate ordinary neutral-control
branch loses health naturally and revives at the owned checkpoint with7 spares;
both real Windows worlds were inspected. No game or save-code correction.
The older383 mismatch restarted its tape at poll0; do not reopen it as a save bug.
No further basic-save or old-build compatibility matrix is required by this gate.

Next select a substantive player-visible first-level fidelity gap using current
source and ordinary play. The known C11372 fallback was inspected read-only;
no nearest-pose mapping was promoted for pixel alignment/art detail alone.
Do not turn hypothetical/unobserved cases into instrument-only fixes. Optional
player-visible feedback was requested asynchronously; no answer is assumed.'''
assert old in text;text=text.replace(old,new)
text=text.replace('- Final-life/menu/current saves:', '- Current Available MD save/retry: [focused qualification](pride-current-save-retry.md).\n- Final-life/menu/current saves:')
text=text.replace('Latest source archive409 preserves the former handoff/status; current aggregate\nis `build/pride410-audit/report.json`. All404..408 runs are terminal.','Latest source archive415 preserves the410 handoff/status; current aggregate\nis `build/pride416-bindings/report.json`. All411/414 runs are terminal.')
path.write_text(text,encoding='utf-8')
path=ROOT/'docs/pride-lands-status.md';text=path.read_text(encoding='utf-8').replace('Current410,','Current416,',1)
old='| Basic saves/retries | Earlier current-format menu/audio/gameplay evidence exists; full Available MD state written at6000 in406 | Full preset current-combination cold save/retry still unqualified. No old development-save compatibility requirement. |'
new='| Basic saves/retries |411 actual published/default-data arena save and exact cold continuation through level completion;414 natural nonfinal death/owned-checkpoint revival, inspected Windows worlds | Basic full-preset current save/retry gate closed. One ordinary path, no old-save or slot/source/width/mode matrix. [Details](pride-current-save-retry.md). |'
assert old in text;text=text.replace(old,new)
old='''1. Qualify one ordinary current-build save/retry with the full Available MD
   profile. Keep recorded polled-input bookkeeping correct;383's poll0 restart
   after loading3750 does not prove a save bug.
2. Investigate a naturally visible remaining first-level difference when one is'''
new='''1. Basic current save/retry is qualified by411/414; do not repeat it without a
   connected change or reported defect.411 correctly slices the3279 consumed
   polled inputs, resolving the old harness ambiguity without a game fix.
2. Investigate a naturally visible remaining first-level difference when one is'''
assert old in text;text=text.replace(old,new)
text=text.replace('- [Prepared gameplay](pride-prepared-gameplay.md),','- [Current save/retry](pride-current-save-retry.md).\n- [Prepared gameplay](pride-prepared-gameplay.md),')
path.write_text(text,encoding='utf-8')
path=ROOT/'engine/docs/devlog.md';text=path.read_text(encoding='utf-8')
text+='\n\n## Current Available MD save/retry411..416\n\n411 PASS12 uses published398/default installed data, ordinary current arena save\nat3600,3279 consumed polls and correctly sliced cold continuation. Guest endpoint\nsamples/final whole client/entire resumed PCM match uninterrupted406; reaches\nlevel1 with8 spares. Resumed actual Windows arena inspected.414 PASS5 follows32\nrecorded polls then neutral controls: natural health death, one spare consumed,\nhealth6 and world restored at1200/112 with7 spares. Actual revived Windows world\ninspected. No guest edits or game/save/runtime changes, no unrelated matrix.\n413 read-only fallback art inspection promotes no nearest-pose/pixel-detail fix.\n415 archives handoff410;416 closes the concrete basic full-preset save/retry gate.\nBroader original fidelity remains scoped/unqualified; first-level goal stays OPEN.\nSee root docs/pride-current-save-retry.md.\n'
path.write_text(text,encoding='utf-8')
paths=[Path(__file__),*reports,ROOT/'build/pride413-cub-frame/report.json',*[ROOT/name for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-current-save-retry.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1')]]
out=ROOT/'build/pride416-bindings';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='PROGRESS_GOAL_OPEN',previous_goal_turn='progress',full_first_level_complete=False,basic_full_preset_save_retry_complete=True,runtime_changed=False,remaining='Broader original MD first-level action/effect/voice/fall fidelity remains unqualified; prioritize substantive natural player-visible differences, not pixel/instrument-only refinement.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('Basic full-preset current save/retry gate closed; no game code changed, goal open.')
