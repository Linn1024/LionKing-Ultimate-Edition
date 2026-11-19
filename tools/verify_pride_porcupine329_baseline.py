"""Compare the changed MD-audio path against its own preceding source choice."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/pride-porcupine328/report.json';r=bound(reference)
out=ROOT/'build/pride-porcupine329-baseline';out.mkdir(exist_ok=True)
cmd=r['commands']['md-voice-new'].copy();cmd[0]=str(ROOT/'build/pride-battle319/player.exe')
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(out/name)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda p:re.findall(pattern,p.read_text())
new=rows(reference.parent/'md-voice-new/run.log');old=rows(out/'run.log');native=rows(reference.parent/'native-new/run.log')
checks={k:v for k,v in r['checks'].items() if k!='md_voice_guest'}
checks.update(old_md_voice_guest_preserved=rc==0 and len(old)==401 and old==new,md_voice_execution_modes=new==rows(reference.parent/'md-voice-lle/run.log'),md_voice_native_pictures=[p[:2] for p in native]==[p[:2] for p in new],audio_timing_changed=digest(out/'audio.wav')!=digest(reference.parent/'md-voice-new/audio.wav'))
paths=[Path(__file__),reference,ROOT/'build/pride-porcupine327/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,voices=r['voices'],scope='Corrected baseline compares MD audio against prior MD audio. Existing native cue interception clears A and changes sound-queue RAM; this change preserves that complete guest history. Native-picture equality separately checked. Failed328 assertion retained; no cross-source full-WRAM equivalence claim.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
