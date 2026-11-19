"""Launch the packaged preview through its actual CMD entry and capture Windows."""
import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-launch2';package_path=base/'preview-package-audit.json';package=bound(package_path)
    exe=ROOT/'dist/development-preview/LionKing.exe';assert digest(exe)==package['binary_sha256'];out=base/'launcher-smoke';out.mkdir()
    launcher=ROOT/'Play Development Preview.cmd';trace=out/'presents.jsonl'
    cmd=['cmd.exe','/d','/c','call',str(launcher),'--no-audio','--no-record','--no-pace','--frames','1601','--menu-at','1600','--menu-page','resources']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};env['TLK_SOFT_TREE_LOG']=str(trace)
    kernel=C.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.argtypes=[W.DWORD,W.BOOL,W.DWORD];kernel.OpenProcess.restype=W.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes=[W.HANDLE,W.DWORD,W.LPWSTR,C.POINTER(W.DWORD)];kernel.CloseHandle.argtypes=[W.HANDLE]
    def game_window():
        found=[];callback=C.WINFUNCTYPE(W.BOOL,W.HWND,W.LPARAM)
        @callback
        def visit(hwnd,unused):
            pid=W.DWORD();USER32.GetWindowThreadProcessId(hwnd,C.byref(pid));handle=kernel.OpenProcess(0x1000,False,pid.value)
            if not handle:return True
            try:
                buf=C.create_unicode_buffer(32768);size=W.DWORD(len(buf))
                if kernel.QueryFullProcessImageNameW(handle,0,buf,C.byref(size)) and Path(buf.value).resolve()==exe.resolve() and window_for(pid.value)==hwnd:found.append(hwnd)
            finally:kernel.CloseHandle(handle)
            return True
        USER32.EnumWindows(visit,0);return found[0] if found else None
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);hwnd=None;deadline=time.monotonic()+120
        try:
            while proc.poll() is None and time.monotonic()<deadline:
                if not hwnd:hwnd=game_window()
                row=latest(trace)
                if hwnd and row and row['field']==1600 and row['about']==2:break
                time.sleep(.02)
            assert hwnd and proc.poll() is None and row['about']==2,('no packaged editor',proc.poll(),latest(trace))
            USER32.SetProcessDPIAware();size=capture_client(hwnd,out/'client.png')
            assert USER32.PostMessageW(hwnd,0x100,0x7b,1);assert USER32.PostMessageW(hwnd,0x101,0x7b,0xc0000001);proc.wait(timeout=30)
        finally:
            if proc.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    choices={c[0]:c for c in row['choices']};settings=ROOT/'settings/development-preview'
    checks=dict(actual_launcher_exit=proc.returncode==0,real_packaged_client_captured=(out/'client.png').exists(),
                md_viewport=row['width']==320 and size==(960,672),health_death_selected=choices['gameplay.levels.pride_lands.health_death'][4]==2,
                independent_art_selected=choices['graphics.sprites.simba.cub.frames'][4]==2,
                independent_music_selected=choices['audio.music.pride_lands'][4]==2,separate_settings_and_boot=(settings/'game.ini').exists() and (settings/'tlk_practice_boot.state').read_bytes()[:8]==b'TLKSTAT1',
                real_paused_resource_tree=row['menu']==1 and row['about']==2 and row['dirty']==0)
    paths=[Path(__file__),package_path,launcher,ROOT/'profiles/pride-development-preview.ini',settings/'game.ini',settings/'resources.ini',ROOT/'tools/verify_pride_soft_tree.py',ROOT/'tools/verify_windows.py',ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,command=cmd,client_size=size,binary_sha256=package['binary_sha256'],
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                experimental_preview=True,default_installed_player_replaced=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
