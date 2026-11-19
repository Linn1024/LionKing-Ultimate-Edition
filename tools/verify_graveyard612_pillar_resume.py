"""Resume the same current pillar effect through impact with equivalent boundary observers."""
import collections,csv,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard602-pillar/report.json';r=bound(reference);build=ROOT/'build/graveyard609/build-report.json';bound(build)
out=ROOT/'build/graveyard612-pillar-resume';out.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(build.parent/'player.exe');i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--load',str(reference.parent/'pending.state')),('--input-polled',str(reference.parent/'pending.polled.tape')),('--hash-at','17000'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json')),('--wav',str(out/'audio.wav')),('--wav-seconds','10')):
    if flag in ('--config','--resource-profile'):Path(value).write_bytes(Path(r['command'][r['command'].index(flag)+1]).read_bytes())
    cmd[cmd.index(flag)+1]=value
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
counts=collections.Counter((x['selector'],x['value']) for x in csv.DictReader((out/'commands.csv').open()));expected=[x for x in csv.DictReader((reference.parent/'stems.csv').open()) if int(x['frame'])>16450];actual=list(csv.DictReader((out/'stems.csv').open()))
checks=dict(impact_once_no_fall_restart=counts=={('2','92'):1},every_remaining_sound_peak=actual==expected,actual_play_preserved=json.loads((out/'scene.json').read_text())['latched_gameplay']==json.loads((reference.parent/'scene.json').read_text())['latched_gameplay'])
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,scope='The same store/group event is observed before it in the interpreter and after it in compiled mode.610 showed no original duplicate in its actual segment and unchanged PCM/picture; this check qualifies the equivalent impact seam and restored long-effect continuation, without claiming a gameplay or audible bug fix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
