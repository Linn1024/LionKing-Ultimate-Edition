"""Reject damaged ordinary saves through real F5 while revival remains live."""
import argparse
import json
from pathlib import Path
import struct
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import environment,read_rows,toast_image
from verify_windows import USER32,window_for,hashes,pixels


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('crc-md','backend-native'),default='crc-md');args=p.parse_args()
    md=args.case=='crc-md';name='md-lle' if md else 'native-aot'
    base=ROOT/'build/pride-practice';out=base/'verified/rejection'/args.case;out.mkdir(parents=True,exist_ok=True)
    assert not (out/'report.json').exists(),'Use a fresh capture directory'
    build_path=base/'build-report.json';build=json.loads(build_path.read_text());binary=base/'practice-sdl.exe'
    for path,sha in build['source_sha256'].items():assert digest(ROOT/path)==sha,path
    assert digest(binary)==build['runs']['sdl']['binary_sha256']
    author=base/'verified/normal-ui'/name;author_path=author/'report.json';r=json.loads(author_path.read_text());assert r['result']=='PASS'
    state=author/'automatic-original.state';raw=bytearray(state.read_bytes());assert raw[:8]==b'PRPRAC01'
    if md:raw[56]^=1
    else:
        raw[256+36]^=1
        raw[56:88]=bytes(32)
        import hashlib
        raw[56:88]=hashlib.sha256(raw).digest()
    profile=out/'resources.ini';profile.write_bytes((author/'resources.ini').read_bytes())
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={}
    def command(name):
        folder=out/name;folder.mkdir(exist_ok=True);config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profile,'--config',config,'--input',tape,'--load',state,'--frames',2100,
            '--no-audio','--no-record','--dump-window',folder/'window.png','--dump-png',folder/'guest.png',
            '--wav',folder/'audio.wav','--wav-seconds',100]
        if md:cmd+=['--lle']
        return folder,list(map(str,cmd))
    control,cmd=command('control');cmd+=['--no-pace'];commands['control']=cmd
    with (control/'run.log').open('wb') as log:
        result=subprocess.run(cmd,cwd=ROOT,env=environment(control),stdout=log,stderr=subprocess.STDOUT,timeout=180)
    assert not result.returncode,result.returncode
    candidate,cmd=command('candidate');commands['candidate']=cmd;(candidate/'tlk_slot1.state').write_bytes(raw)
    USER32.SetProcessDPIAware();until=time.monotonic()+90;hwnd=None;entry=1777 if md else 1776
    with (candidate/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=environment(candidate),stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        while not hwnd:
            hwnd=window_for(proc.pid);assert proc.poll() is None and time.monotonic()<until;time.sleep(.005)
        while True:
            rows=read_rows(candidate/'practice-fields.csv')
            if rows and int(rows[-1]['field'])>=entry+265:break
            assert proc.poll() is None and time.monotonic()<until;time.sleep(.003)
        assert USER32.PostMessageW(hwnd,0x100,116,1);assert USER32.PostMessageW(hwnd,0x101,116,0xc0000001)
        code=proc.wait(timeout=90)
    loads=read_rows(candidate/'live-load.csv');failed=[r for r in loads if r['success']=='0']
    checks=dict(exit=code==0,one_rejection=len(loads)==2 and len(failed)==1,
        field_during_owned=len(failed)==1 and entry+265<=int(failed[0]['attempt_field'])<=entry+274,
        guest=hashes(candidate/'run.log')==hashes(control/'run.log'),pcm=wav_data(candidate/'audio.wav')==wav_data(control/'audio.wav'),
        damaged_slot_unchanged=(candidate/'tlk_slot1.state').read_bytes()==raw)
    for name in ('owner-events.csv','owner-fields.csv','restore-events.csv','restore-fields.csv','post-ready.csv','spawn-policy.csv','bank-clock.csv'):
        checks[name]=read_rows(candidate/name)==read_rows(control/name)
    for name in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv'):
        checks[name]=digest(candidate/'restart-1'/name)==digest(control/'restart-1'/name)
    error='Ordinary-play save is incompatible or damaged' if md else 'State audio continuation is incompatible or damaged'
    expected=toast_image(control/'window.png',control/'guest.png','Slot 1: '+error)
    checks['whole_error_client']=pixels(candidate/'window.png')==expected
    paths=(Path(__file__),build_path,author_path,state,tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py')
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,loads=loads,
        binary_sha256=digest(binary),source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},commands=commands,
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(args.case,report['result'],[n for n,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
