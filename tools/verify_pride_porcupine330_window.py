"""Actual Windows client from the short ordinary porcupine approach."""
import json,os,re,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/pride-porcupine328/report.json';ref=bound(reference)
proof=ROOT/'build/pride-porcupine329-baseline/report.json';assert bound(proof)['result']=='PASS'
out=ROOT/'build/pride-porcupine330-window';out.mkdir(exist_ok=True);cmd=ref['commands']['md-voice-new'].copy()
for flag in ('--wav','--wav-seconds','--dump-window','--dump-scene'):
    i=cmd.index(flag);del cmd[i:i+2]
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_PORCUPINE_VOICE_TRACE']=str(out/'voice.csv')
USER32.SetProcessDPIAware();before=after=None;reader=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(Path(cmd[0]),proc.pid);deadline=time.monotonic()+45
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=1471:
                hwnd=window_for(proc.pid)
                if hwnd:capture_client(hwnd,out/'attack.png');after=reader.snapshot();break
            time.sleep(.002)
        proc.wait(timeout=30)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda p:re.findall(pattern,p.read_text())
checks=dict(exit=proc.returncode==0,actual_window=bool(after) and 1471<=before['field']<=after['field']<1510,guest=rows(out/'run.log')==rows(reference.parent/'md-voice-new/run.log'),cue=(out/'voice.csv').read_bytes()==(reference.parent/'md-voice-new/voice.csv').read_bytes())
paths=[Path(__file__),reference,proof]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,before=before,after=after,command=cmd,scope='Short real Windows attack client and matching guest/cue; no new leaf or UI interaction needed, source setting existing.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
