"""Exercise automatic practice save and actual F1/F5/F9 before any revival."""
import argparse
import json
from pathlib import Path
import struct
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_live_error_ui import environment,read_rows
from verify_windows import USER32,window_for,hashes
from windows_capture import capture_client


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native-aot','md-lle'),default='native-aot')
    p.add_argument('--output-root',type=Path)
    args=p.parse_args();base=ROOT/'build/pride-practice'
    out=(ROOT/args.output_root if args.output_root else base/'ui-pilot')/args.case;out.mkdir(parents=True,exist_ok=True)
    assert not (out/'tlk_practice_boot.state').exists(),'Use a fresh capture directory'
    build_path=base/'build-report.json';build=json.loads(build_path.read_text());binary=base/'practice-sdl.exe'
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==build['runs']['sdl']['binary_sha256']
    source_profile=ROOT/f'build/pride-restart-clock/final/windows/{args.case}/resources.ini'
    profile=out/'resources.ini';profile.write_bytes(source_profile.read_bytes())
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--resource-profile',profile,'--config',config,'--speedrun','practice','--practice-level',0,'--frames',1700,
        '--no-audio','--no-record','--dump-window',out/'window.png','--dump-png',out/'guest.png',
        '--wav',out/'audio.wav','--wav-seconds',100]
    if args.case=='md-lle':command+=['--lle']
    USER32.SetProcessDPIAware();hwnd=None;observations={};until=time.monotonic()+120
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(list(map(str,command)),cwd=ROOT,env=environment(out),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        def wait_for(predicate):
            while not predicate():
                assert proc.poll() is None,('Game ended before required observation',proc.returncode)
                assert time.monotonic()<until,('Observation deadline; inspect existing process',proc.pid)
                time.sleep(.005)
        def key(code):
            assert USER32.PostMessageW(hwnd,0x100,code,1)
            assert USER32.PostMessageW(hwnd,0x101,code,0xc0000001)
        while not hwnd:
            hwnd=window_for(proc.pid);assert proc.poll() is None and time.monotonic()<until;time.sleep(.005)
        restart=out/'tlk_practice_restart.state';slot=out/'tlk_slot1.state'
        wait_for(restart.exists);data=restart.read_bytes();assert data[:8]==b'PRPRAC01'
        observations['automatic_saved_field']=struct.unpack_from('<I',data,20)[0]
        (out/'automatic-original.state').write_bytes(data)
        time.sleep(.12);key(112);wait_for(slot.exists)
        data=slot.read_bytes();assert data[:8]==b'PRPRAC01'
        observations['manual_saved_field']=struct.unpack_from('<I',data,20)[0]
        time.sleep(.12);key(116)
        wait_for(lambda:len(read_rows(out/'live-load.csv'))>=2)
        time.sleep(.12);capture_client(hwnd,out/'slot-toast.png')
        time.sleep(.12);key(120)
        wait_for(lambda:len(read_rows(out/'live-load.csv'))>=3)
        time.sleep(.12);capture_client(hwnd,out/'restart-toast.png')
        code=proc.wait(timeout=90)
    loads=read_rows(out/'live-load.csv')
    checks=dict(exit=code==0,three_loads=len(loads)==3 and all(r['success']=='1' for r in loads),
        manual_field=len(loads)>=2 and int(loads[1]['loaded_field'])==observations['manual_saved_field'],
        restart_field=len(loads)>=3 and int(loads[2]['loaded_field'])==observations['automatic_saved_field'],
        restart_file_unchanged=restart.read_bytes()==(out/'automatic-original.state').read_bytes(),
        no_owned_scene=not read_rows(out/'owner-events.csv'))
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,source_profile,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/windows_capture.py')}
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,observations=observations,loads=loads,
        binary_sha256=digest(binary),source_sha256=sources,command=list(map(str,command)),guest=hashes(out/'run.log'),
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],checks,observations,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
