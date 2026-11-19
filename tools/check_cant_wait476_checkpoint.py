"""Try an existing ride fixture unchanged; do not add old-save compatibility."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait452-checkpoint/report.json';r=bound(reference);assert r['result']=='READY'
build=ROOT/'build/cant-wait473/build-report.json';bound(build)
out=ROOT/'build/cant-wait476-checkpoint';out.mkdir(exist_ok=True);cmd=r['resume_command'].copy();cmd[0]=str(build.parent/'player.exe')
m=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'));cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'game-data'/m['sprite_assets']['file'])
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','resumed.png'),('--dump-scene','scene.json')):
    old=Path(cmd[cmd.index(flag)+1]);cmd[cmd.index(flag)+1]=str(out/name)
    if flag in ('--config','--resource-profile'):(out/name).write_bytes(old.read_bytes())
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW).returncode
scene=json.loads((out/'scene.json').read_text()) if (out/'scene.json').exists() else None
ready=rc==0 and scene and scene['level']==1 and scene['latched_gameplay']['descriptor']==0x3b9
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='USABLE' if ready else 'UNSUITABLE_NO_COMPAT_WORK',exit_code=rc,command=cmd,scope='One cheap existing-fixture load. Use it only if the unmodified current loader accepts and resumes in the ride; no migration, bypass or compatibility fix. If unsuitable use level select for further work.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('ride fixture', 'USABLE' if ready else 'UNSUITABLE',rc,flush=True)
