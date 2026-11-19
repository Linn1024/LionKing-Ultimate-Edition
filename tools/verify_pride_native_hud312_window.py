"""Short installed cold-save Windows view plus a one-field candidate launch."""
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
reference=ROOT/'build/pride-native-hud309-runtime/report.json';ref=bound(reference)
package=ROOT/'dist/installed-preview307/package-report.json';bound(package)
data=ROOT/'build/pride-native-hud310-setup';manifest=data/'install.json';m=json.loads(manifest.read_text())
out=ROOT/'build/pride-native-hud312-window';out.mkdir();checks={};cmd=ref['commands']['cold'].copy();cmd[0]=str(package.parent/'LionKing.exe')
cmd.remove('--no-pace');cmd[cmd.index('--frames')+1]='2300'
for flag in ('--dump-window','--dump-scene'):
    i=cmd.index(flag);del cmd[i:i+2]
for flag,key in (('--rom','snes'),('--md-rom','megadrive')):
    spec=m['roms'][key];p=data/spec['file'];assert digest(p)==spec['sha256'];cmd[cmd.index(flag)+1]=str(p)
for flag,key in (('--asset-cache','scene_cache'),('--final-menu-assets','menu_assets'),('--final-native-assets','native_final_assets'),('--title-bank-assets','title_bank_assets'),('--hud-assets','hud_assets'),('--sprite-assets','sprite_assets'),('--caption-assets','caption_assets'),('--checkpoint-assets','checkpoint_assets'),('--revival-assets','revival_assets'),('--native-hud-assets','native_hud_assets')):
    spec=m[key];p=data/spec['file'];assert digest(p)==spec['sha256'];cmd[cmd.index(flag)+1]=str(p)
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};USER32.SetProcessDPIAware();hwnd=None;reader=None
with (out/'window.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(package.parent/'LionKing.exe',proc.pid);deadline=time.monotonic()+30
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=2060:
                hwnd=window_for(proc.pid)
                if hwnd:break
            time.sleep(.003)
        assert hwnd;before['prepared_native_hud_pointer']=reader.value('prepared_native_hud')
        capture_client(hwnd,out/'meters.png');after=reader.snapshot()
    finally:
        if reader:reader.close()
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
checks['actual_current_save_window']=2060<=before['field']<=after['field']<2150 and proc.returncode==0
checks['prepared_native_meter_copy_observed']=bool(before['prepared_native_hud_pointer'])
checks['prepared_glyphs_loaded']='native_hud_assets=loaded' in (out/'window.log').read_text()
settings=out/'launcher-settings';launcher=ROOT/'build/pride-native-hud307-installed/RunInstalledPreviewCandidate.ps1'
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
launch=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(launcher),'-DataDirectory',str(data),'-SettingsDirectory',str(settings),'-Frames','1','-NoPace','-NoAudio']
with (out/'launcher.log').open('wb') as log:rc=subprocess.run(launch,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW).returncode
checks['candidate_launcher_passes_required_glyph_package']=rc==0 and 'native_hud_assets=loaded' in (settings/'last-launch.log').read_text()
paths=[Path(__file__),reference,package,manifest,launcher,ROOT/'scripts/Setup.ps1',ROOT/'build/pride-native-hud306-helper/tlk_prepare_native_hud_assets.exe']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,launcher_command=launch,before=before,after=after,
    scope='Actual Setup data and packaged player restore a fresh same-build revival save; one Windows meter client and prepared font pointer observed. One-field candidate launcher verifies new required argument. No repeated full-route Windows capture or unrelated suite.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',before['field'],after['field'],checks,flush=True)
