"""Aggregate completed practical second-level delivery, preserving explicit native limits."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
names=['cant-wait566-animation-cues','cant-wait573-route-audio','cant-wait574-native-control','cant-wait575-current-save','cant-wait580-continue-audio','cant-wait581-audio-ui','cant-wait584-pause','cant-wait586-publication']
proofs=[ROOT/'build'/name/'report.json' for name in names]
results={name:bound(path)['result'] for name,path in zip(names,proofs)}
assert all(result==('VERIFIED' if name=='cant-wait566-animation-cues' else 'PASS') for name,result in results.items())
build=ROOT/'build/cant-wait579/build-report.json';b=bound(build);exe=ROOT/'dist/installed-preview579/LionKing.exe';launcher=ROOT/'scripts/RunInstalledPreview.ps1'
assert digest(exe)==b['binary_sha256'] and "'dist/installed-preview579'" in launcher.read_text()
paths=[Path(__file__),build,launcher,ROOT/'docs/cant-wait-sound-delivery.md',ROOT/'docs/cant-wait-sound-gameplay-goal.md',ROOT/'docs/HANDOFF.md',ROOT/'docs/second-level-goal.md',ROOT/'docs/cant-wait-delivery-review.md',ROOT/'docs/next-levels-status.md',ROOT/'engine/docs/devlog.md',*proofs]
out=ROOT/'build/cant-wait587-delivery';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='PASS',published=True,practical_second_level_goal_complete=True,gameplay='Native retained by user direction; no concrete ordinary-play blocker established; universal MD gameplay equivalence not claimed',sounds='Eight independent level-specific effects plus shared Simba/Continue/checkpoint choices and preexisting independent music',evidence=results,checks=dict(full_level_route=True,native_control=True,current_save=True,actual_pause_resume=True,actual_resource_editor_restart=True,installed_launch=True,settings_assets_preserved=True),limits='No whole-runtime ROM independence, rare-case certification, all-original-rules selectable or device-listening onset equality claim; shared hurt uses existing mapping, without separate naturally injured CW recording',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('DELIVERED',b['binary_sha256'],flush=True)
