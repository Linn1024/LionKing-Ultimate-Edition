"""Inspect the ostrich ride after a real camera wrap with live MD scenery."""
import json,os,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/cant-wait362/build-report.json';bound(build)
out=ROOT/'build/cant-wait365-ride';out.mkdir(exist_ok=True)
ref=json.loads((ROOT/'build/hyena-hud357/report.json').read_text());cmd=ref['command'].copy();cmd[0]=str(build.parent/'player.exe')
cmd[cmd.index('--input-polled')+1]=str(ROOT/'engine/tapes/allbugsF.read.tape')
cmd[cmd.index('--frames')+1]='6350';cmd[cmd.index('--hash-at')+1]='6200,6216,6350'
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(out/name)
cmd+=['--save-at','6350',str(out/'ride.state')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
scene=json.loads((out/'scene.json').read_text());raw=(out/'ride.state').read_bytes();at=raw.find(b'TLKVIEW1');state=struct.unpack_from('<9I',raw,at+80)
checks=dict(exit=rc==0,in_second_level=scene['level']==1 and scene['stage_detected'],background_active=state[0]==1,palette_transition_complete=state[1]==1 and state[3]==100,camera_wrap_retained=state[7]>0 and state[8]>0)
paths=[Path(__file__),build,ROOT/'engine/tapes/allbugsF.read.tape']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,view_state=state,scope='One ordinary full-controller prefix to the ostrich ride and real camera wrap; inspect scene with mixed foreground/objects. No full-game hash/equality matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,state,flush=True)
