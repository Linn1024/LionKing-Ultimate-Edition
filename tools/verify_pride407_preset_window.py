"""Inspect the full Available MD boss scene in an ordinary Windows replay."""
import json,os,re,struct,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/pride406-preset-route/report.json';r=bound(reference);assert r['result']=='PASS'
out=ROOT/'build/pride407-preset-window';out.mkdir(exist_ok=True);cmd=r['command'].copy()
i=cmd.index('--save-at');del cmd[i:i+3]
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(out/name)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};USER32.SetProcessDPIAware();reader=None;before=after=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(Path(cmd[0]),proc.pid);deadline=time.monotonic()+90
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=4400:
                hwnd=window_for(proc.pid)
                if hwnd:capture_client(hwnd,out/'boss.png');after=reader.snapshot();break
            time.sleep(.005)
        proc.wait(timeout=90)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda p:re.findall(pattern,p.read_text());scene=json.loads((out/'scene.json').read_text())
checks=dict(exit=proc.returncode==0,actual_boss_window=bool(after) and 4400<=before['field']<=after['field']<4700,guest_samples_equal=rows(out/'run.log')==rows(reference.parent/'run.log'),final_picture_equal=digest(out/'window.png')==digest(reference.parent/'window.png'),whole_pcm_equal=digest(out/'audio.wav')==digest(reference.parent/'audio.wav'),first_level_completed=scene['level']==1,no_life_lost=scene['latched_gameplay']['lives']==8)
paths=[Path(__file__),reference,ROOT/'build/pride398/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,before=before,after=after,scope='One ordinary power-on full Available MD route in a real window, original boss-scene client inspected, next level reached with all8 spare lives. Same complete input/profile as406, selected guest samples/final client/PCM exact. No loaded states, guest edits, practice or unrelated source matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
