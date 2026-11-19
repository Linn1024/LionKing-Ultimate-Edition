"""Read-only callback context capture from the current candidate's ordinary route."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

base=ROOT/'build/pride-hyena-probe97';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride-hyena-probe101';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
source=ROOT/'tools/pride_hyena_probe_observer101.c';cmd=b['compiles']['probe'].copy()
for flag,value in [('-c',source),('-o',out/'observer.obj'),('-MT',out/'observer.obj'),('-MF',out/'observer.d')]:cmd[cmd.index(flag)+1]=str(value)
subprocess.run(cmd,cwd=cwd,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];inputs.insert(0,(out/'observer.obj').as_posix());inputs+=['-Wl,--wrap=TlkHyenaWalkingProbe']
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,check=True)
prior=bound(ROOT/'build/pride-menu-enable86/route/report.json');cmd=prior['commands']['menus-aot'].copy();cmd[0]=str(out/'player.exe')
for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
with (out/'resources.ini').open('a') as f:f.write('\ngameplay.levels.pride_lands.hyena_probe_height = md\n')
for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
env.update(SDL_VIDEODRIVER='dummy',TLK_HYENA_PROBE_OBSERVER=str(out/'contexts.csv'))
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
paths=[Path(__file__),bp,source,rsp]
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED' if rc==0 else 'FAIL',exit=rc,command=cmd,read_only_wrapper=True,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Observer exit',rc,flush=True)
