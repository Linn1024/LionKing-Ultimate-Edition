"""Observe real F1 save/F5 rejected-load UI during a current private revival."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import USER32,window_for,hashes,pixels
from windows_capture import capture_client
from verify_pride_audio_state import wav_data


def main():
    base=ROOT/'build/pride-handoff-state';out=ROOT/'build/pride-live-error-ui/pilot';out.mkdir(parents=True,exist_ok=True)
    binary=base/'handoff-state-sdl.exe';build_path=base/'build-report.json';build=json.loads(build_path.read_text())
    assert digest(binary)==build['runs']['sdl']['binary_sha256']
    for file,sha in build['source_sha256'].items():assert digest(ROOT/file)==sha,file
    reference=base/'windows/md-default-320-all-0-lle-aot';r=json.loads((reference/'report.json').read_text());assert r['result']=='PASS'
    for file,sha in r['source_sha256'].items():assert digest(ROOT/file)==sha,file
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    command=list(r['commands']['resumed'])
    command[command.index('--config')+1]=str(config)
    for flag,file in (('--dump-window','window.png'),('--wav','audio.wav')):command[command.index(flag)+1]=str(out/file)
    command.remove('--no-pace');command+=['--dump-png',str(out/'guest.png')]
    env=os.environ.copy()
    for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(out)
    for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE','TLK_SCENE_RESTORE_ENABLE',
                'TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
    env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
    USER32.SetProcessDPIAware();slot=out/'tlk_slot1.state';assert not slot.exists(),'Use a fresh capture directory'
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        hwnd=None
        try:
            until=time.monotonic()+45
            def field():
                try:
                    with (out/'restore-fields.csv').open() as f:rows=list(csv.DictReader(f))
                    return int(rows[-1]['field']) if rows and rows[-1].get('field') else 0
                except (OSError,ValueError,KeyError):return 0
            def wait_for(target):
                while field()<target:
                    assert time.monotonic()<until and proc.poll() is None
                    time.sleep(.003)
            def key(value):
                assert USER32.PostMessageW(hwnd,0x100,value,1)
                assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001)
            while not hwnd:
                hwnd=window_for(proc.pid);assert proc.poll() is None and time.monotonic()<until;time.sleep(.005)
            wait_for(1777+267);key(112)
            while not slot.exists():
                assert time.monotonic()<until and proc.poll() is None;time.sleep(.003)
            original=slot.read_bytes();saved=struct.unpack_from('<I',original,20)[0]
            assert original[:8]==b'PRHSAVE1' and 1777+267<=saved<=1777+272,saved
            (out/'saved-valid.state').write_bytes(original)
            damaged=bytearray(original);damaged[0]^=1;slot.write_bytes(damaged)
            wait_for(saved+5);attempted=field();key(116)
            time.sleep(.08);capture_client(hwnd,out/'error-live.png')
            proc.wait(timeout=25)
        finally:
            if proc.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    checks=dict(exit=proc.returncode==0,guest=hashes(out/'run.log')==r['runs']['resumed']['guest'],
        native_pcm=wav_data(out/'audio.wav')==wav_data(reference/'resumed/audio.wav'))
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,reference/'report.json',reference/'revival.private-state',
        ROOT/'tools/windows_capture.py',ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py')}
    report=dict(result='OBSERVED',checks=checks,save_field=saved,f5_requested_field=attempted,
        command=command,binary_sha256=digest(binary),source_sha256=sources,
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'},
        actual_f1_f5_used=True,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
