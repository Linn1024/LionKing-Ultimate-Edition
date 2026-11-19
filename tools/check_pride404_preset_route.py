"""One ordinary walkthrough using the exact draft from the Available MD UI."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride398/build-report.json';bound(build)
ui=ROOT/'build/pride401-ui/report.json';u=bound(ui);assert u['result']=='PASS'
reference=ROOT/'build/pride392-route/report.json';r=bound(reference)
out=ROOT/'build/pride404-preset-route';out.mkdir(exist_ok=True)
cmd=r['commands']['after'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
sources=('inherit','snes','md');preset=u['snapshots']['preset']['choices']
(out/'resources.ini').write_text('schema = 1\n'+'\n'.join(c[0]+' = '+sources[c[1]] for c in preset)+'\n')
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(out/name)
cmd+=['--save-at','5000',str(out/'endpoint.state')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
scene=json.loads((out/'scene.json').read_text());game=scene['latched_gameplay']
checks=dict(exit=rc==0,exact_actual_ui_preset=True,profile_accepted='Saved resource profile loaded' in (out/'run.log').read_text(),first_level_completed=scene['level']==1,simba_alive=game['health']>0)
paths=[Path(__file__),build,ui,reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE_ROUTE',checks=checks,command=cmd,endpoint=dict(level=scene['level'],gameplay=game,camera=scene['camera']),scope='One ordinary power-on credited controller route with the exact actual Available MD UI draft and independent native unsupported overrides. No guest/ROM edits, practice or loaded state. A route endpoint is not proof of all original MD behaviors.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,scene['level'],game,flush=True)
