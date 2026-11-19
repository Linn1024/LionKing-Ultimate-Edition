"""Check the published launcher, actual Windows client and obsolete prepared-policy rejection."""
import json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
publication=ROOT/'build/graveyard631-publication/report.json';bound(publication)
out=ROOT/'build/graveyard632-installed';out.mkdir();settings=out/'settings';settings.mkdir();(settings/'resources.ini').write_bytes((ROOT/'build/graveyard623-gameplay/resources.ini').read_bytes())
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe');base=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/RunInstalledPreview.ps1')]
old=base+['-DataDirectory',str(ROOT/'build/graveyard538-setup/data'),'-SettingsDirectory',str(out/'obsolete-settings'),'-Frames','1','-NoAudio','-NoPace']
with (out/'obsolete.log').open('wb') as log:result=subprocess.run(old,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
checks=dict(obsolete_policy_rejected=result.returncode!=0 and 'Setup' in (out/'obsolete.log').read_text())
cmd=base+['-SettingsDirectory',str(settings),'-PracticeLevel','2','-Frames','1800','-NoPace','-NoAudio','-SceneCapture',str(out/'scene.json'),'-WindowCapture',str(out/'window.png')]
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name;USER32.SetProcessDPIAware();captured=False
with (out/'launch.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+35
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row and row['field']>=1580 and row['level']==2 and not captured:
                # Powershell is the parent; obtain the launched player PID from the current process inventory.
                query=subprocess.check_output([ps,'-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \"Name='LionKing.exe'\" | Select-Object -ExpandProperty ProcessId"],creationflags=subprocess.CREATE_NO_WINDOW,text=True)
                for pid in query.split():
                    hwnd=window_for(int(pid))
                    if hwnd:capture_client(hwnd,out/'actual-client.png');captured=True;break
            time.sleep(.008)
        proc.wait(timeout=10)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish()
last=trace.latest();choices={x[0]:x for x in last['choices']};scene=json.loads((out/'scene.json').read_text())
checks.update(clean_installed_launch=proc.returncode==0,actual_client=captured,correct_living_level=scene['level']==2 and scene['latched_gameplay']['health']>0,both_sources_selected=all(choices['gameplay.levels.elephant_graveyard.'+name][4]==2 for name in ('vulture_health','vulture_bounds')),prepared_assets_loaded='sprite_assets=loaded' in (settings/'last-launch.log').read_text())
paths=[Path(__file__),publication,ROOT/'scripts/RunInstalledPreview.ps1',ROOT/'game-data/install.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,obsolete_command=old,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
