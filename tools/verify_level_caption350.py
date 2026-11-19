"""Check the corrected entrance validator and inspect a genuine Windows title."""
import json,os,re,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
build=ROOT/'build/level-caption349/build-report.json';bound(build)
prior=ROOT/'build/level-caption347/report.json';ref=bound(prior)
out=ROOT/'build/level-caption350';out.mkdir(exist_ok=True);commands={};checks={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for case in ('falling','settled'):
    folder=out/case;folder.mkdir(exist_ok=True)
    if case=='falling':template=ref['commands']['falling-new'];old=prior.parent/'falling-old'
    else:template=json.loads((ROOT/'build/level-caption346/report.json').read_text())['command'];old=ROOT/'build/level-caption341/2'
    cmd=template.copy();cmd[0]=str(build.parent/'player.exe')
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):
        if flag in cmd:cmd[cmd.index(flag)+1]=str(folder/name)
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=dict(clean,SDL_VIDEODRIVER='dummy'),stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda p:re.findall(pattern,p.read_text())
    checks[case+'_guest']=rc==0 and bool(rows(folder/'run.log')) and rows(folder/'run.log')==rows(old/'run.log')
    checks[case+'_changed']=digest(folder/'window.png')!=digest(old/'window.png')
    if case=='settled':checks['settled_exact_previous_corrected_picture']=digest(folder/'window.png')==digest(ROOT/'build/level-caption346/window.png')
    commands[case]=cmd
folder=out/'windows';folder.mkdir(exist_ok=True);cmd=commands['settled'].copy()
for flag in ('--wav','--dump-window','--dump-scene'):
    if flag in cmd:i=cmd.index(flag);del cmd[i:i+2]
cmd[cmd.index('--frames')+1]='1650';USER32.SetProcessDPIAware();reader=None;before=after=None
with (folder/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(Path(cmd[0]),proc.pid);deadline=time.monotonic()+30
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=1550:
                hwnd=window_for(proc.pid)
                if hwnd:capture_client(hwnd,folder/'caption.png');after=reader.snapshot();break
            time.sleep(.002)
        proc.wait(timeout=20)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
checks['actual_windows_client']=proc.returncode==0 and bool(after) and 1550<=before['field']<=after['field']<1570
checks['prior_narrow_and_pride_controls_passed']=all(v for k,v in ref['checks'].items() if k.startswith(('narrow','pride')))
paths=[Path(__file__),build,prior,ROOT/'build/level-caption346/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,window_command=cmd,before=before,after=after,scope='Corrected both native entrance directions; changed falling picture, unchanged guest, stable title reproduces exact corrected glyph picture. Prior narrow/Pride controls reused; one actual Windows client.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
