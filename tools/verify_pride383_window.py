"""Qualify the sole frontend guard change and inspect a current fight window."""
import json,os,re,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
build=ROOT/'build/pride382/build-report.json';bound(build)
reference=ROOT/'build/pride381-route/report.json';ref=bound(reference)
assert all(v for k,v in ref['checks'].items() if k!='outdated_data_requests_setup')
out=ROOT/'build/pride383-window';out.mkdir(exist_ok=True)
old=(ROOT/'build/pride-porcupine327/frontend/sdl_main.c').read_text();new=(build.parent/'frontend/sdl_main.c').read_text()
guard='    if(asset_cache && !prepare_resources && !TlkResourcesCachePrepared()) {\n        fprintf(stderr,"Installed scene data could not be loaded. Run Setup.cmd again.\\n");free(rom);return 8;\n    }\n'
assert new.replace(guard,'')==old
cmd=ref['commands']['after'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,n in (('--save-at',3),('--wav',2)):
    i=cmd.index(flag);del cmd[i:i+n]
cmd[cmd.index('--frames')+1]='3852';cmd[cmd.index('--hash-at')+1]='3852';cmd.remove('--no-pace')
cmd+=['--load',str(reference.parent/'after/fight.state')]
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
            if before['field']>=3810:
                hwnd=window_for(proc.pid)
                if hwnd:capture_client(hwnd,out/'fight.png');after=reader.snapshot();break
            time.sleep(.003)
        proc.wait(timeout=10)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
expected=[r for r in re.findall(pattern,(reference.parent/'after/run.log').read_text()) if r[0]=='3852']
reject=ref['reject_command'].copy();reject[0]=cmd[0];env['SDL_VIDEODRIVER']='dummy'
with (out/'rejected.log').open('wb') as log:rc=subprocess.run(reject,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW).returncode
checks=dict(route_gameplay_picture_audio=all(v for k,v in ref['checks'].items() if k!='outdated_data_requests_setup'),only_early_error_guard_added=True,current_fight_exit=proc.returncode==0,current_fight_guest=re.findall(pattern,(out/'run.log').read_text())==expected,actual_window=bool(after) and 3810<=before['field']<=after['field']<3852,outdated_cache_reports_scene_error=rc==8 and 'Installed scene data could not be loaded' in (out/'rejected.log').read_text() and 'caption data is missing' not in (out/'rejected.log').read_text())
paths=[Path(__file__),build,reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,reject_command=reject,before=before,after=after,scope='381 route completed with gameplay/picture/audio exact; its failed obsolete-cache exit classification led to the sole early error guard in382. Current fight continuation and real Windows capture, corrected scene error. No repeated route/full-game/source matrix.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
