"""Qualify unchanged completed148 captures after an obsolete PCM reference path."""
import csv
import json
from pathlib import Path
import re
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
raw=base/'routes148';attempt=raw/'attempt-report.json';assert not attempt.exists()
for name in ('verify_pride_hyena_entrance148_routes.py','verify_pride_hyena_probe99_routes.py'):shutil.copy2(ROOT/'tools'/name,raw/name)
artifacts={p.relative_to(raw).as_posix():digest(p) for p in raw.rglob('*') if p.is_file()}
attempt.write_text(json.dumps(dict(result='FAIL',reason='All three routes completed with level1. Verifier then referenced prior menus-aot/audio.wav instead of probe-aot/audio.wav; no final report written. Raw outputs retained.',artifacts_sha256=artifacts),indent=2)+'\n')
reference=ROOT/'build/pride-resource-tree118/routes99/report.json';prior=bound(reference);assert prior['result']=='PASS'
out=base/'routes154-qualification';out.mkdir();checks={};commands={};observations={}
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
for name in ('native','probe-aot','probe-lle'):
    folder=raw/name;log=(folder/'run.log').read_text();scene=json.loads((folder/'scene.json').read_text())
    rows=list(csv.DictReader((folder/'probes.csv').open())) if (folder/'probes.csv').exists() else []
    checks[name+'_full_route_to_next_level']='result=completed frames=6000' in log and scene['level']==1 and len(hashes(folder))==6000
    checks[name+'_scoped_entrance_operands']=not rows if name=='native' else len(rows)==1002 and all(int(r['selected_operand'])==int(r['camera_x'])+64 for r in rows)
    cmd=prior['commands']['probe-aot'].copy();cmd[0]=str(base/'player.exe')
    profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()+'\ngameplay.levels.pride_lands.hyena_entrance_window = '+('snes' if name=='native' else 'md')+'\n'
    assert (folder/'resources.ini').read_text()==profile
    assert (folder/'host.ini').read_bytes()==Path(cmd[cmd.index('--config')+1]).read_bytes()
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
    if name.endswith('lle'):cmd+=['--lle']
    commands[name]=cmd;observations[name]=dict(level=scene['level'],adjustments=len(rows))
control=raw/'native';a=raw/'probe-aot';bb=raw/'probe-lle'
checks['native_all6000_guest_fields_preserved']=hashes(control)==hashes(reference.parent/'probe-aot')
checks['native_whole_pcm_preserved']=digest(control/'audio.wav')==digest(reference.parent/'probe-aot/audio.wav')
checks['selected_all6000_guest_mode_parity']=hashes(a)==hashes(bb)
for file in ('window.png','scene.json','audio.wav','probes.csv'):checks[file+'_selected_mode_parity']=digest(a/file)==digest(bb/file)
checks['new_leaf_compiled_available']='-DTLK_HYENA_ENTRANCE_AVAILABLE=1' in b['compiles']['resources']
paths=[Path(__file__),bp,reference,attempt,*[p for p in raw.rglob('*') if p.is_file()]]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,commands_reconstructed_from_frozen_verifier_and_retained_profiles=True,
    correction='Original148 verifier stopped after completed captures at a stale prior PCM path. These checks qualify unchanged logs/media/profiles, correcting only that reference. No rerun or overwritten failed evidence. Actual native/MD entrance selection completes; original timer trajectory and Windows remain separately scoped.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
