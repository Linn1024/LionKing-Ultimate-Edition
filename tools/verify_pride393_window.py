"""Inspect installed table-backed ordinary play and outdated sprite rejection."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/pride392-route/report.json';ref=bound(reference);assert ref['result']=='PASS'
build=ROOT/'build/pride390/build-report.json';bound(build)
out=ROOT/'build/pride393-window';out.mkdir(exist_ok=True);cmd=ref['commands']['after'].copy()
i=cmd.index('--wav');del cmd[i:i+2]
cmd[cmd.index('--frames')+1]='2000';cmd[cmd.index('--hash-at')+1]='2000'
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(out/name)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};USER32.SetProcessDPIAware();reader=None;before=after=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(Path(cmd[0]),proc.pid);deadline=time.monotonic()+60
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=1700:
                hwnd=window_for(proc.pid)
                if hwnd:capture_client(hwnd,out/'play.png');after=reader.snapshot();break
            time.sleep(.003)
        proc.wait(timeout=60)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
manifest=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'))
reject=cmd.copy();reject[reject.index('--sprite-assets')+1]=str(ROOT/'game-data'/manifest['sprite_assets']['file']);reject[reject.index('--frames')+1]='1'
env['SDL_VIDEODRIVER']='dummy'
with (out/'rejected.log').open('wb') as log:rc=subprocess.run(reject,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW).returncode
scene=json.loads((out/'scene.json').read_text())
checks=dict(exit=proc.returncode==0,actual_window=bool(after) and 1700<=before['field']<=after['field']<2000,ordinary_first_level=scene['level']==0 and scene['stage_detected'],old_sprite_package_requests_setup=rc==6 and 'Installed sprite data is missing or incompatible' in (out/'rejected.log').read_text(),profile_accepted='Profile rejected' not in (out/'run.log').read_text())
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,reject_command=reject,before=before,after=after,scope='Ordinary power-on play with prepared tables, actual Windows client inspected; old sprite-v1 rejected before play with Setup instruction. No save/mode/width matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
