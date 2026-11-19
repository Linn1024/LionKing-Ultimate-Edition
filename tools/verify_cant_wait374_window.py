"""Inspect the prepared foreground in a real window after a current moving save."""
import json,os,re,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/cant-wait373/report.json';ref=bound(reference);assert ref['result']=='PASS'
out=ROOT/'build/cant-wait374-window';out.mkdir(exist_ok=True);cmd=ref['commands']['moving'].copy()
for flag,n in (('--practice-level',2),('--save-at',3),('--wav',2)):
    i=cmd.index(flag);del cmd[i:i+n]
cmd+=['--load',str(reference.parent/'moving.state')];cmd.remove('--no-pace')
cmd[cmd.index('--hash-at')+1]='2200'
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(out/name)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};USER32.SetProcessDPIAware();reader=None;before=after=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(Path(cmd[0]),proc.pid);deadline=time.monotonic()+20
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=2140:
                hwnd=window_for(proc.pid)
                if hwnd:capture_client(hwnd,out/'foreground.png');after=reader.snapshot();break
            time.sleep(.003)
        proc.wait(timeout=10)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda p:re.findall(pattern,p.read_text())
checks=dict(exit=proc.returncode==0,current_save_guest=rows(out/'run.log')==[r for r in rows(reference.parent/'moving/run.log') if r[0]=='2200'],current_save_picture=digest(out/'window.png')==digest(reference.parent/'moving/window.png'),actual_window=bool(after) and 2140<=before['field']<=after['field']<2200)
paths=[Path(__file__),reference,ROOT/'build/cant-wait372/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,before=before,after=after,scope='One current moving save restores the prepared MD foreground and palette; native guest and client exact at endpoint, real Windows foreground/monkey view inspected. No legacy or unrelated matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
