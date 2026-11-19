"""Prepare menu and native payloads through the actual Windows Setup button."""
import ctypes as C
from ctypes import wintypes as W
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import USER32,ENUM
from windows_capture import capture_client


def main():
    out=ROOT/'build/pride-final-native-installed/window';out.mkdir();data=out/'GUI installed data'
    command=['powershell','-NoProfile','-STA','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/Setup.ps1'),'-DataDirectory',str(data)]
    USER32.SetProcessDPIAware();hwnd=None;checks={};deadline=time.monotonic()+90
    def title(handle):
        text=C.create_unicode_buffer(512);USER32.GetWindowTextW(handle,text,len(text));return text.value
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while not hwnd:
                assert proc.poll() is None and time.monotonic()<deadline
                found=[]
                @ENUM
                def each(handle,unused):
                    owner=W.DWORD();USER32.GetWindowThreadProcessId(handle,C.byref(owner))
                    if owner.value==proc.pid and title(handle)=='Lion King PC Setup':found.append(handle)
                    return True
                USER32.EnumWindows(each,0);hwnd=found[0] if found else None;time.sleep(.03)
            def children():
                found=[]
                @ENUM
                def each(handle,unused):found.append((handle,title(handle)));return True
                USER32.EnumChildWindows(hwnd,each,0);return found
            time.sleep(.2);capture_client(hwnd,out/'before.png')
            button=next(h for h,text in children() if text=='Prepare game data')
            assert USER32.PostMessageW(button,0xf5,0,0)
            while not (data/'install.json').exists() or not any(text=='Prepare again' for h,text in children()):
                assert proc.poll() is None and time.monotonic()<deadline;time.sleep(.03)
            time.sleep(.2);capture_client(hwnd,out/'ready.png')
            manifest=json.loads((data/'install.json').read_text());menu=data/manifest['menu_assets']['file']
            native=data/manifest['native_final_assets']['file']
            checks['button_completed']=any(text=='Prepare again' for h,text in children())
            checks['prepared_package_digest']=digest(menu)==manifest['menu_assets']['sha256']
            checks['prepared_native_digest']=digest(native)==manifest['native_final_assets']['sha256']
            checks['native_payload_count']=manifest['native_final_assets']['payloads']==10 and len(native.read_bytes())==131582
            checks['ready_message']=any('Ready.' in text for h,text in children())
        finally:
            if proc.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks['clean_exit']=proc.returncode==0
    paths=[Path(__file__),ROOT/'scripts/Setup.ps1']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=command,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
