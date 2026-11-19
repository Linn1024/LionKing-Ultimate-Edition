"""Replay the live countdown-divergence route in production139 and both modes."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
decision=ROOT/'build/pride-hyena-entrance153-live-decision/report.json';d=bound(decision);assert d['result']=='PASS'
reference=ROOT/'build/pride-hyena-entrance157-drop/report.json';ref=bound(reference);assert ref['result']=='CAPTURED'
out=base/'boundary159';out.mkdir();commands={};checks={};case=d['case']
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
for name,source in [('native',case+'-snes'),('selected-aot',case+'-md'),('selected-lle',case+'-md')]:
    folder=out/name;folder.mkdir();cmd=ref['commands'][source].copy();cmd[0]=str(base/'player.exe')
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
    for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
    if name.endswith('lle'):cmd+=['--lle']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
    with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    commands[name]=cmd
    checks[name+'_exit_and4194_fields']=rc==0 and len(hashes(folder))==4194
    checks[name+'_all_guest_fields_match_observed_route']=hashes(folder)==hashes(reference.parent/source)
    for file in ('window.png','scene.json','audio.wav'):checks[name+'_'+file+'_match_observed_route']=digest(folder/file)==digest(reference.parent/source/file)
    print(name,'exit',rc,'observer guest equality',checks[name+'_all_guest_fields_match_observed_route'],flush=True)
checks['selected_all_guest_fields_mode_parity']=hashes(out/'selected-aot')==hashes(out/'selected-lle')
checks['binary_exact']=digest(base/'player.exe')==b['binary_sha256']
paths=[Path(__file__),bp,decision,reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Ordinary full power-on route with only the entrance-window gameplay leaf changed. Production native/selected results reproduce observed actual timer divergence via all4194 full guest hashes and media. Selected compiled/interpreted route exact. No original whole-MD trajectory or all-AI claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
