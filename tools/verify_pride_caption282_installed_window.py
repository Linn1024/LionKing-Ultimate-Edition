"""One actual installed-launcher opening caption using the real Setup result."""
import json
import os
from pathlib import Path
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client

package=ROOT/'dist/installed-preview277/package-report.json';bound(package)
data=ROOT/'build/pride-caption280-setup';manifest=data/'install.json';m=json.loads(manifest.read_text());caption=data/m['caption_assets']['file']
assert digest(caption)==m['caption_assets']['sha256']==digest(ROOT/'build/pride-caption277-installed/captions.assets')
out=ROOT/'build/pride-caption282-window';out.mkdir();settings=out/'settings';settings.mkdir()
(settings/'game.ini').write_text('opengl = 0\nscale = 2\n');(settings/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n')
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
launcher=ROOT/'build/pride-caption277-installed/RunInstalledPreviewCandidate.ps1'
cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(launcher),'-DataDirectory',str(data),'-SettingsDirectory',str(settings),'-Frames','1500','-NoAudio','-InputTape',str(ROOT/'build/pride-caption270-clamp/idle.polled.tape')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};hwnd=None;reader=None;USER32.SetProcessDPIAware()
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+70;child=None
        while proc.poll() is None and time.monotonic()<deadline and not child:
            query=f"Get-CimInstance Win32_Process -Filter 'ParentProcessId = {proc.pid}' | Where-Object Name -eq 'LionKing.exe' | Select-Object -ExpandProperty ProcessId"
            result=subprocess.check_output([ps,'-NoProfile','-Command',query],creationflags=subprocess.CREATE_NO_WINDOW,timeout=10).decode().strip()
            if result:child=int(result.splitlines()[0])
        assert child;reader=PlayerRead(package.parent/'LionKing.exe',child)
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=1030:
                hwnd=window_for(child)
                if hwnd:break
            time.sleep(.005)
        assert hwnd;capture_client(hwnd,out/'caption.png');after=reader.snapshot()
    finally:
        if reader:reader.close()
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=15)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
checks=dict(actual_setup_package_matches_preparation=digest(caption)==m['caption_assets']['sha256'],clean_launcher_exit=proc.returncode==0,
    prepared_caption_load='caption_assets=loaded' in (settings/'last-launch.log').read_text(),actual_caption_interval=1030<=before['field']<=after['field']<1150)
paths=[Path(__file__),package,manifest,caption,launcher,ROOT/'scripts/Setup.ps1',ROOT/'build/pride-caption276-helper/tlk_prepare_caption_assets.exe']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,before=before,after=after,
    scope='Actual Setup-produced package, manifest validation and installed candidate launcher, one own-child Windows opening caption. No unrelated broad suite.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
