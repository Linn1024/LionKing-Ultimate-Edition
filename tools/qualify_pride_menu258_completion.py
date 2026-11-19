"""Qualify completed252 captures using the corrected156 route evidence rules."""
import csv
import json
from pathlib import Path
import re
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

base=ROOT/'build/pride-menu226-integrated';build_path=base/'build-report.json';build=bound(build_path)
raw=base/'routes252';attempt=raw/'attempt-report.json';assert not attempt.exists()
for name in ('verify_pride_menu252_completion.py','verify_pride_hyena_entrance148_routes.py','verify_pride_hyena_probe99_routes.py'):
    shutil.copy2(ROOT/'tools'/name,raw/name)
attempt.write_text(json.dumps(dict(result='FAIL',reason='All three players exited0 at level1, then the inherited148 verifier used its obsolete menus-aot/audio.wav reference. Capture bytes retained unchanged; no recapture.',
    artifacts_sha256={p.relative_to(raw).as_posix():digest(p) for p in raw.rglob('*') if p.is_file()}),indent=2)+'\n')
reference=ROOT/'build/pride-resource-tree118/routes99/report.json';prior=bound(reference)
out=ROOT/'build/pride-menu258-completion';out.mkdir();checks={};commands={};observations={}
observation=dict(tool='functions.exec / tools.write_stdin',session_id=44648,verifier_exit_code=1,
    observed_stdout=['native exit 0 level 1 probes 0','probe-aot exit 0 level 1 probes 1002','probe-lle exit 0 level 1 probes 1002'],
    player_exit_codes=dict(native=0,**{'probe-aot':0,'probe-lle':0}),recorded_by='root from actual session output; not inferred from log completion markers')
(out/'process-observation.json').write_text(json.dumps(observation,indent=2)+'\n')
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
for name in ('native','probe-aot','probe-lle'):
    folder=raw/name;scene=json.loads((folder/'scene.json').read_text());fields=rows(folder)
    probes=list(csv.DictReader((folder/'probes.csv').open())) if (folder/'probes.csv').exists() else []
    checks[name+'_completed_next_level']=observation['player_exit_codes'][name]==0 and scene['level']==1 and [int(r[0]) for r in fields]==list(range(1,6001))
    checks[name+'_actual_entrance_operands']=not probes if name=='native' else len(probes)==1002 and all(int(r['selected_operand'])==int(r['camera_x'])+64 for r in probes)
    cmd=prior['commands']['probe-aot'].copy();cmd[0]=str(base/'player.exe')
    profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()+'\ngameplay.levels.pride_lands.hyena_entrance_window = '+('snes' if name=='native' else 'md')+'\n'
    assert (folder/'resources.ini').read_text()==profile
    assert (folder/'host.ini').read_bytes()==Path(cmd[cmd.index('--config')+1]).read_bytes()
    for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/file)
    if name.endswith('lle'):cmd+=['--lle']
    commands[name]=cmd;observations[name]=dict(level=scene['level'],entrance_calls=len(probes))
a=raw/'probe-aot';b=raw/'probe-lle';control=raw/'native'
checks['native_all6000_guest_fields_preserved']=rows(control)==rows(reference.parent/'probe-aot')
checks['native_whole_pcm_preserved']=digest(control/'audio.wav')==digest(reference.parent/'probe-aot/audio.wav')
checks['selected_all6000_guest_mode_parity']=rows(a)==rows(b)
for file in ('window.png','scene.json','audio.wav','probes.csv'):checks[file+'_selected_mode_parity']=digest(a/file)==digest(b/file)
checks['entrance_choice_compiled_available']='-DTLK_HYENA_ENTRANCE_AVAILABLE=1' in build['compiles']['resources']
paths=[Path(__file__),build_path,reference,attempt,*[p for p in raw.rglob('*') if p.is_file()]]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
    commands_reconstructed_from_frozen_verifier_and_retained_profiles=True,
    scope='Unchanged252 completed ordinary mixed routes, actual observed process exits, all6000 sequential guest fields, next main level, whole PCM and mode media. Correct stale inherited PCM path using established156 rules; no rerun, old evidence overwritten or full first-level equivalence claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'process-observation.json':digest(out/'process-observation.json')}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
