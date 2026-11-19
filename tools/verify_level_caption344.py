"""Focused two-line title presentation with unchanged guest state."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/level-caption343/build-report.json';bound(build)
out=ROOT/'build/level-caption344';out.mkdir(exist_ok=True)
reference=ROOT/'build/level-caption341/report.json';ref=json.loads(reference.read_text());cmd=ref['commands']['2'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(out/name)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda p:re.findall(pattern,p.read_text());old=reference.parent/'2'
checks=dict(exit=rc==0,guest=bool(rows(out/'run.log')) and rows(out/'run.log')==rows(old/'run.log'),native_audio=digest(out/'audio.wav')==digest(old/'audio.wav'),presentation_changed=digest(out/'window.png')!=digest(old/'window.png'),scene_unchanged=digest(out/'scene.json')==digest(old/'scene.json'))
paths=[Path(__file__),build,reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,scope='Same ordinary Elephant Graveyard opening with native falling glyphs and unchanged guest/audio. Inspect whole client for per-line centring; no broad gameplay suites.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
