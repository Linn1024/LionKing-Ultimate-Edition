"""Real F1 with visible practice UI must save the same UI-free owned record."""
import argparse
import json
from pathlib import Path
import struct
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment, read_rows
from verify_pride_audio_state import wav_data
from verify_windows import USER32, window_for, hashes
from windows_capture import capture_client


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native','md-media'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-practice-live'; author=base/args.case; author_path=author/'report.json'; prior=bound(author_path)
    assert prior['result']=='PASS' and all(prior['checks'].values())
    binary=base/'runtime/practice-live.exe'; dll=base/'runtime/genesis_plus_gx_libretro.dll'
    assert digest(binary)==prior['binary_sha256'] and digest(dll)==prior['dll_sha256']
    out=base/'owned-ui-save'/args.case;out.mkdir(parents=True,exist_ok=True);assert not (out/'report.json').exists()
    state=author/'baseline/tlk_practice_restart.state'; profile=out/'resources.ini';profile.write_bytes((author/'resources.ini').read_bytes())
    commands={};target=prior['revival_begins'][0]+225
    def command(name):
        folder=out/name;folder.mkdir(exist_ok=True);config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input',ROOT/'build/pride-repeated-route/oscillate/ordinary.tape',
             '--load',state,'--speedrun','practice','--frames',2100,'--no-audio','--no-record',
             '--dump-window',folder/'window.png','--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',100]
        if args.case=='md-media':cmd+=['--lle']
        return folder,list(map(str,cmd))
    live,cmd=command('live');commands['live']=cmd;slot=live/'tlk_slot1.state'
    USER32.SetProcessDPIAware();hwnd=None;until=time.monotonic()+120
    with (live/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=environment(live),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while not hwnd:
                hwnd=window_for(proc.pid);assert proc.poll() is None and time.monotonic()<until;time.sleep(.005)
            while True:
                rows=read_rows(live/'practice-fields.csv')
                if rows and int(rows[-1]['field'])>=target:break
                assert proc.poll() is None and time.monotonic()<until;time.sleep(.003)
            assert USER32.PostMessageW(hwnd,0x100,112,1);assert USER32.PostMessageW(hwnd,0x101,112,0xc0000001)
            while not slot.exists():
                assert proc.poll() is None and time.monotonic()<until;time.sleep(.003)
            raw=slot.read_bytes();assert raw[:8]==b'PRHSAVE1';saved=struct.unpack_from('<I',raw,20)[0]
            time.sleep(.04);capture_client(hwnd,live/'saved-toast.png');code=proc.wait(timeout=90)
        finally:
            if proc.poll() is None:
                USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    control,cmd=command('control');explicit=control/'explicit.state';cmd+=['--no-pace','--save-at',str(saved),str(explicit)];commands['control']=cmd
    with (control/'run.log').open('wb') as log:
        r=subprocess.run(cmd,cwd=ROOT,env=environment(control),stdout=log,stderr=subprocess.STDOUT,timeout=150)
    checks=dict(exit=code==r.returncode==0,actual_f1=target<=saved<=target+8,
        whole_ui_free_record=raw==explicit.read_bytes(),guest=hashes(live/'run.log')==hashes(control/'run.log'),
        pcm=wav_data(live/'audio.wav')==wav_data(control/'audio.wav'),
        save_message='Saved slot 1' in (live/'run.log').read_text())
    for name in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','ground-entry.bin','ground-return.bin'):
        checks[name]=digest(live/'restart-1'/name)==digest(control/'restart-1'/name)
    paths=(Path(__file__),author_path,state,profile,ROOT/'tools/windows_capture.py',ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py')
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,saved_field=saved,
        binary_sha256=digest(binary),dll_sha256=digest(dll),source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},commands=commands,
        artifacts_sha256={str(q.relative_to(out)).replace('\\','/'):digest(q) for q in out.rglob('*') if q.is_file() and q.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
