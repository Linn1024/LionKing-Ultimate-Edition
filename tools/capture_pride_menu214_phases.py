"""Observe native YES phase boundaries and preserve current210 guest/media."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_final_scene_runtime import pcm
reference=ROOT/'build/pride-menu210-continue/report.json';ref=bound(reference)
assert ref['result']=='CAPTURED'
build=ROOT/'build/pride-menu213-phases/build-report.json';bound(build)
out=ROOT/'build/pride-menu214-phases';out.mkdir()
cmd=ref['commands']['yes'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
for flag,file in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
env.update(SDL_VIDEODRIVER='dummy',TLK_MENU197=str(out/'menu.csv'),TLK_MENU_CURSOR208=str(out/'cursor.csv'))
with (out/'run.log').open('wb') as f:
    rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW).returncode
rows=list(csv.DictReader((out/'menu.csv').open()))
events=[r for r in rows if r['kind'] not in ('frame','FinalInputHold','FinalInputDecision')]
control=reference.parent/'yes';pattern=r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
checks=dict(exit=rc==0,all2501_guest_samples_exact=re.findall(pattern,(out/'run.log').read_text())==re.findall(pattern,(control/'run.log').read_text()),
    whole_pcm_exact=pcm(out/'audio.wav')==pcm(control/'audio.wav'),client_exact=digest(out/'window.png')==digest(control/'window.png'),
    scene_exact=(out/'scene.json').read_bytes()==(control/'scene.json').read_bytes(),three_native_stages_observed=all(any(r['kind']==k for r in rows) for k in ('NativeExitStart','NativeExitWait','NativeReloadStart')))
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,events=events,
    scope='Read-only original native YES phase callbacks on the fresh ordinary credit-bearing route; unchanged sampled guest/media vs210.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,events,flush=True)
