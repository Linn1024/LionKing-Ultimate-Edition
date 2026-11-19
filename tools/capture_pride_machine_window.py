"""Capture the OS game client during play after an owned MD reset."""
import json
from pathlib import Path
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_windows import USER32,window_for,hashes,pixels
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-machine-player4';matrix_path=base/'md/report.json';matrix=bound(matrix_path);assert matrix['result']=='PASS'
    build_path=base/'build-report.json';build=bound(build_path);binary=base/'machine.exe';assert digest(binary)==build['binary_sha256']
    out=base/'os-window';out.mkdir();author=base/'md/soft-aot'
    command=[s.replace(str(author),str(out)) for s in matrix['commands']['soft-aot']]
    (out/'host.ini').write_bytes((author/'host.ini').read_bytes())
    env=environment(out);env.update(TLK_MACHINE_RESET_AT='2002',TLK_MACHINE_RESET_KIND='soft',TLK_AUDIO_STEMS=str(out/'stems.csv'),TLK_MD_SOUND_COMMANDS=str(out/'md-commands.csv'))
    USER32.SetProcessDPIAware();captured=None;hwnd=None
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline=time.monotonic()+180
            while proc.poll() is None and time.monotonic()<deadline:
                if hwnd is None:hwnd=window_for(proc.pid)
                if captured is None and hwnd and (out/'machine-boundary.json').exists():
                    rows=read_rows(out/'practice-fields.csv')
                    if rows and 1450<=int(rows[-1]['field'])<1700:
                        captured=dict(before_field=int(rows[-1]['field']),size=capture_client(hwnd,out/'client.png'))
                        print('OS client captured after reset at',captured['before_field'],flush=True)
                time.sleep(.02)
            proc.wait(timeout=5);assert proc.returncode==0,proc.returncode
        finally:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
    assert captured,'No post-reset OS client captured'
    for path in out.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(path)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
    w,h,p=pixels(out/'client.png')
    checks=dict(os_viewport=(w,h)==(640,448),os_picture_nonblank=len(set(p))>128,
                final_guest=hashes(out/'run.log')==hashes(author/'run.log'),
                whole_final_client=pixels(out/'window.png')==pixels(author/'window.png'),
                entire_recorded_pcm=wav_data(out/'audio.wav')==wav_data(author/'audio.wav'))
    assert all(checks.values()),checks
    paths=[Path(__file__),matrix_path,build_path,ROOT/'tools/windows_capture.py',ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py']
    report=dict(result='PASS',checks=checks,capture=captured,command=command,binary_sha256=digest(binary),
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS OS client',checks,flush=True)


if __name__=='__main__':main()
