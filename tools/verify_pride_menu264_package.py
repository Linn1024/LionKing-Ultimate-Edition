"""One focused installed-launcher smoke: visible gameplay and the new menu leaf."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from windows_capture import capture_client
from windows_json_pipe import JsonPipe

package=ROOT/'dist/installed-preview260/package-report.json';bound(package)
base=ROOT/'build/pride-menu260-help';launcher=base/'RunInstalledPreviewCandidate.ps1'
out=ROOT/'build/pride-menu264-package';out.mkdir();settings=out/'settings';settings.mkdir()
seed=ROOT/'build/pride-menu257-md-source-ui'
for src,dst in (('host.ini','game.ini'),('resources.ini','resources.ini')):shutil.copy2(seed/src,settings/dst)
protected={p.name:digest(p) for p in settings.iterdir()}
ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
cmd=[ps,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(launcher),'-SettingsDirectory',str(settings),'-Frames','3600','-InputTape',str(ROOT/'engine/tapes/allbugsF.read.tape'),'-NoAudio']
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
checks={};snapshots={};hwnd=None;child=None;USER32.SetProcessDPIAware()
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+100
        while not child and proc.poll() is None and time.monotonic()<deadline:
            query=f"Get-CimInstance Win32_Process -Filter 'ParentProcessId = {proc.pid}' | Where-Object Name -eq 'LionKing.exe' | Select-Object -ExpandProperty ProcessId"
            result=subprocess.check_output([ps,'-NoProfile','-Command',query],creationflags=subprocess.CREATE_NO_WINDOW,timeout=10).decode().strip()
            if result:child=int(result.splitlines()[0])
        assert child
        def wait(predicate):
            while proc.poll() is None and time.monotonic()<deadline:
                row=trace.latest()
                if row and predicate(row):return row
                time.sleep(.01)
            raise AssertionError(('Package window condition missing',proc.poll(),trace.latest()))
        before=wait(lambda r:r['field']>=2600 and r['descriptor']==0xc00387 and r['health']>0);snapshots['game']=before
        hwnd=window_for(child);assert hwnd;capture_client(hwnd,out/'game.png')
        def key(vk):
            scan=USER32.MapVirtualKeyW(vk,0);extra=0x1000000 if 0x21<=vk<=0x28 else 0
            assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16)+extra)
            assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16)+extra)
            time.sleep(.055)
        key(0x7b);row=wait(lambda r:r['about']==2)
        node='graphics.pride_final_menu';key(0x24)
        for _ in range(180):
            row=trace.latest();name=row['choices'][row['selected']][0]
            if name==node:break
            if name=='game' or node.startswith(name+'.'):key(0x27)
            key(0x28)
        assert name==node;capture_client(hwnd,out/'new-node.png');snapshots['node']=row
        checks['installed_gameplay_visible']=before['descriptor']==0xc00387 and before['health']>0
        checks['new_leaf_reachable_with_MD_art_selected']=row['about']==2 and next(c[-1] for c in row['choices'] if c[0]==node)==2
        checks['installed_cache_loaded']='resource_cache=loaded' in '' # finalized after launcher writes its log
    finally:
        if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
        try:proc.wait(timeout=15)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish();(out/'trace-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
checks['installed_cache_loaded']='resource_cache=loaded' in (settings/'last-launch.log').read_text()
checks['settings_preserved']=all(digest(settings/name)==sha for name,sha in protected.items())
checks['clean_launcher_exit']=proc.returncode==0
paths=[Path(__file__),package,launcher,ROOT/'game-data/install.json',ROOT/'tools/windows_json_pipe.py']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,snapshots=snapshots,process_child=child,
    scope='One installed candidate launcher run with default prepared game data: actual Pride world and new resource leaf inspected in Windows, settings retained. No broad regression rerun; underlying226 gameplay/media gates plus260 help-only provenance retained.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
