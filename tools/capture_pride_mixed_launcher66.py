"""Inspect the mixed-graphics CMD's actual descendant window and default choices."""
import json
import os
from pathlib import Path
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from verify_pride_soft_tree import latest
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-launchers66';source=base/'report.json';prior=bound(source);assert prior['result']=='PASS'
    out=base/'windows';out.mkdir();settings=out/'settings';trace=out/'tree.jsonl'
    cmd=['cmd.exe','/d','/c','call',str(ROOT/'Play Mixed Graphics.cmd'),'-SettingsDirectory',str(settings),'-Frames','3000',
         '-InputTape',str(ROOT/'engine/tapes/allbugsF.read.tape'),'-NoAudio']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=str(trace)
    powershell=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
    checks={};hwnd=None;child=None;USER32.SetProcessDPIAware()
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=out,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        deadline=time.monotonic()+90
        try:
            while not child and proc.poll() is None and time.monotonic()<deadline:
                query="$all=Get-CimInstance Win32_Process; $parents=@("+str(proc.pid)+"); for($depth=0;$depth -lt 3;$depth++) { $next=@($all | Where-Object { $parents -contains $_.ParentProcessId }); $game=@($next | Where-Object Name -eq 'LionKing.exe'); if($game) { $game[0].ProcessId; break }; $parents=@($next.ProcessId) }"
                result=subprocess.check_output([powershell,'-NoProfile','-Command',query],env=env,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
                if result:child=int(result.splitlines()[0])
            assert child,'owned player descendant missing'
            def wait(predicate):
                while proc.poll() is None and time.monotonic()<deadline:
                    row=latest(trace)
                    if row and predicate(row):return row
                    time.sleep(.01)
                raise AssertionError(('mixed window condition missing',latest(trace)))
            before=wait(lambda r:r['field']>=2200 and r['descriptor']==0xc00387 and r['health']>0)
            hwnd=window_for(child);assert hwnd;capture_client(hwnd,out/'game.png')
            vk=0x7b;scan=USER32.MapVirtualKeyW(vk,0)
            assert USER32.PostMessageW(hwnd,0x100,vk,1+(scan<<16));assert USER32.PostMessageW(hwnd,0x101,vk,0xc0000001+(scan<<16))
            menu=wait(lambda r:r['about']==2);capture_client(hwnd,out/'resources.png')
            choice=lambda key:next(c[-1] for c in menu['choices'] if c[0]==key)
            checks['actual_cmd_from_other_working_directory']=proc.poll() is None
            checks['live_pride_after_fade']=before['descriptor']==0xc00387 and before['health']>0
            checks['md_view_and_scenery']=choice('display.viewport')==choice('graphics.scenery')==2 and menu['width']==320
            checks['md_palette_native_frames']=choice('graphics.sprites.simba.cub.palette')==2 and choice('graphics.sprites.simba.cub.frames')==1
            checks['native_gameplay_and_audio']=choice('gameplay')==choice('audio.music.pride_lands')==1
            checks['real_resource_menu']=menu['about']==2 and menu['dirty']==0
        finally:
            if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
            try:proc.wait(timeout=15)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_cmd_exit']=proc.returncode==0
    paths=[Path(__file__),source,ROOT/'Play Mixed Graphics.cmd',ROOT/'scripts/RunInstalledPreview.ps1',ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,before=before,menu=menu,
        own_process_tree_only=True,new_settings_and_implicit_caches_owned=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
