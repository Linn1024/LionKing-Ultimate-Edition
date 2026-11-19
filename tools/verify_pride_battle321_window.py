"""Short real Windows view of the corrected opening cue from a current save."""
import csv,json,os,re,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/pride-battle320/report.json';ref=bound(reference);assert ref['result']=='PASS'
out=ROOT/'build/pride-battle321-window';out.mkdir(exist_ok=True)
cmd=ref['commands']['md-new'].copy()
for flag,n in (('--save-at',3),('--wav',2),('--wav-seconds',2),('--dump-window',2),('--dump-scene',2)):
    i=cmd.index(flag);del cmd[i:i+n]
cmd.remove('--no-pace');cmd+=['--load',str(reference.parent/'current-battle.state')]
cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(3846,3881)))
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_BATTLE_MUSIC_TRACE']=str(out/'jump.csv')
USER32.SetProcessDPIAware();reader=None;before=after=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(Path(cmd[0]),proc.pid);deadline=time.monotonic()+20
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=3853:
                hwnd=window_for(proc.pid)
                if hwnd:
                    capture_client(hwnd,out/'opening.png');after=reader.snapshot();break
            time.sleep(.002)
        proc.wait(timeout=15)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda p:re.findall(pattern,p.read_text())
jump=list(csv.DictReader((out/'jump.csv').open())) if (out/'jump.csv').exists() else []
checks=dict(exit=proc.returncode==0,real_window=bool(after) and 3853<=before['field']<=after['field']<=3880,cold_jump=jump==ref['jumps']['md-new'],cold_guest=rows(out/'run.log')==[r for r in rows(reference.parent/'md-new/run.log') if int(r[0])>=3846],compiled_interpreter_pcm=digest(reference.parent/'md-new/audio.wav')==digest(ROOT/'build/pride-battle318/md-lle/audio.wav'))
paths=[Path(__file__),reference,ROOT/'build/pride-battle319/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,before=before,after=after,jump=jump,scope='Short current-build cold restoration around opening jump; actual Windows client capture and guest hashes. No unrelated route replay.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
