"""Drive the real turbo key and check its panel against independent RGB/font math."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_windows import USER32,window_for,hashes,pixels
from windows_capture import capture_client


def turbo_picture(path):
    w,h,base=pixels(path);assert h==448 and w in (512,640)
    font=(ROOT/'engine/runner/tlk_font8x8.h').read_text();glyphs=[[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]+)',row)] for row in re.findall(r'\{([^{}]+)\}',font)]
    assert len(glyphs)==95
    extra=(w//2-256)//2
    for y in range(4,20):
        for x in range(208,252):
            white=False
            if 8<=y<16 and 212<=x<244:
                char='>>4x'[(x-212)//8];white=bool(glyphs[ord(char)-32][y-8]&(1<<((x-212)%8)))
            for dy in (0,1):
                for dx in (0,1):
                    at=(y*2+dy)*w+(extra+x)*2+dx;base[at]=(255,255,255) if white else tuple(c*25//255 for c in base[at])
    return w,h,base


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native','md'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-singlepass';build_path=base/'build-report.json';build=bound(build_path);binary=base/'singlepass.exe';assert digest(binary)==build['binary_sha256']
    out=base/'turbo'/args.case;out.mkdir(parents=True);md=args.case=='md';author=ROOT/'build/pride-source-live/seeded/resources.ini'
    profile=out/'resources.ini';profile.write_bytes(author.read_bytes() if md else b'schema = 1\ngame = snes\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={};capture=None
    for name in ('control','candidate'):
        folder=out/name;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\nturbo_speed = 4\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,'--config',config,'--input',tape,'--frames',1600,'--no-audio','--no-record','--dump-window',folder/'window.png','--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(1,1601)))]
        if md:cmd+=['--lle']
        if name=='control':cmd+=['--no-pace']
        commands[name]=list(map(str,cmd));env=environment(folder);env['TLK_SINGLEPASS_LOG']=str(folder/'presents.csv')
        with (folder/'run.log').open('wb') as log:
            if name=='control':
                r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180);assert not r.returncode
            else:
                USER32.SetProcessDPIAware();proc=subprocess.Popen(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                hwnd=None;deadline=time.monotonic()+120
                try:
                    while proc.poll() is None and time.monotonic()<deadline:
                        if hwnd is None:hwnd=window_for(proc.pid)
                        rows=read_rows(folder/'practice-fields.csv')
                        if hwnd and rows and int(rows[-1]['field'])>=1450:break
                        time.sleep(.003)
                    assert hwnd and proc.poll() is None,'No live turbo target'
                    at=int(rows[-1]['field']);assert 1450<=at<1470,at
                    assert USER32.PostMessageW(hwnd,0x100,0xc0,0x00290001)
                    time.sleep(.08);capture=dict(key_field=at,size=capture_client(hwnd,folder/'client.png'))
                    proc.wait(timeout=120);assert not proc.returncode,proc.returncode
                finally:
                    if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        print(args.case,name,'exit0',flush=True)
    a,b=out/'control',out/'candidate';pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    fields=lambda f:re.findall(pattern,(f/'run.log').read_text())
    presents=read_rows(b/'presents.csv');control_presents=read_rows(a/'presents.csv')
    checks=dict(actual_turbo_key=capture is not None,all_native_fields=fields(a)==fields(b) and len(fields(b))==1600,
                complete_recorded_pcm=wav_data(a/'audio.wav')==wav_data(b/'audio.wav'),
                whole_client_oracle=pixels(b/'window.png')==turbo_picture(a/'window.png'),
                one_overlay_pass=bool(presents) and all(r['toast_calls']=='1' for r in presents),
                turbo_skips_presentations=len(presents)<len(control_presents),os_client_captured=(b/'client.png').is_file())
    paths=[Path(__file__),build_path,author,tape,ROOT/'engine/runner/tlk_font8x8.h',ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_windows.py',ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,capture=capture,commands=commands,binary_sha256=digest(binary),
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
