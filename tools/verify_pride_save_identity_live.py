"""Use real F5 to load an unchanged owned save from the other editor build."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_overlay import mixed_toast
from verify_pride_soft_tree import latest
from verify_windows import USER32,window_for,pixels
from windows_capture import capture_client


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',choices=('native','md'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-save-identity2';build_path=base/'build-report.json';build=bound(build_path);md=args.profile=='md'
    root=base/'verified'/args.profile;author=root/'author-a/owned.state';warm=root/'author-b/owned.state';entry=int.from_bytes(author.read_bytes()[20:24],'little');end=entry+60
    out=base/'live'/args.profile;out.mkdir(parents=True);config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n');slot=out/'tlk_slot1.state';shutil.copy2(author,slot);before=digest(slot)
    exe=base/'b.exe';assert digest(exe)==build['runs']['b']['binary_sha256'];tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    common=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--resource-profile',root/'resources.ini','--input',tape,
            '--frames',end,'--no-audio','--no-record','--speedrun','practice','--hash-at',','.join(map(str,range(entry+1,end+1)))];commands={}
    if md:common+=['--lle']
    for name,state in (('control',author),('live',warm)):
        folder=out/name;folder.mkdir();cmd=common+['--load',state,'--dump-window',folder/'window.png','--dump-png',folder/'guest.png','--wav',folder/'audio.wav','--wav-seconds',100]
        if name=='control':cmd+=['--no-pace']
        commands[name]=list(map(str,cmd));env=environment(folder);trace=folder/'presents.jsonl';env['TLK_SOFT_TREE_LOG']=str(trace);env['TLK_AUDIO_STEMS']=str(folder/'stems.csv')
        with (folder/'run.log').open('wb') as log:
            if name=='control':
                r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120);assert not r.returncode
            else:
                proc=subprocess.Popen(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW);deadline=time.monotonic()+60;hwnd=None
                try:
                    while proc.poll() is None and time.monotonic()<deadline:
                        if not hwnd:hwnd=window_for(proc.pid)
                        row=latest(trace)
                        if hwnd and row and row['field']>=entry+10:break
                        time.sleep(.003)
                    assert hwnd and proc.poll() is None and row['field']<entry+20
                    assert USER32.PostMessageW(hwnd,0x100,0x74,1);assert USER32.PostMessageW(hwnd,0x101,0x74,0xc0000001)
                    time.sleep(.1);USER32.SetProcessDPIAware();capture_client(hwnd,folder/'client.png');proc.wait(timeout=90);assert not proc.returncode
                finally:
                    if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
    a,b=out/'control',out/'live';events=read_rows(b/'live-load.csv');assert len(events)==2 and all(r['success']=='1' for r in events),events
    attempt=int(events[-1]['attempt_field']);pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)';fields=lambda f:re.findall(pattern,(f/'run.log').read_text())
    expected=fields(a);prefix=[r for r in expected if int(r[0])<=attempt]
    journal=read_rows(a/'practice-fields.csv');cut=int(next(r for r in journal if int(r['field'])==attempt+1)['wav_frames_before_audio'])*4
    stems=read_rows(a/'stems.csv');checks=dict(actual_cross_build_f5=entry+10<=attempt<entry+22 and events[-1]['loaded_field']==str(entry),
        all_guest_fields=fields(b)==prefix+expected,complete_pcm=wav_data(b/'audio.wav')==wav_data(a/'audio.wav')[:cut]+wav_data(a/'audio.wav'),
        all_md_stems=read_rows(b/'stems.csv')==[r for r in stems if int(r['frame'])<=attempt]+stems,
        final_guest=pixels(a/'guest.png')==pixels(b/'guest.png'),whole_client_oracle=pixels(b/'window.png')==mixed_toast(a/'window.png','Loaded slot 1'),
        source_save_unmodified=digest(author)==before==digest(slot))
    for folder in (a,b):
        rows=[json.loads(line) for line in (folder/'presents.jsonl').read_text().splitlines()];checks[folder.name+'/one_overlay_pass']=bool(rows) and all(r['passes']==1 for r in rows)
        for file in folder.rglob('*.rgb'):subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(file)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
    paths=[Path(__file__),build_path,author,warm,root/'report.json',tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_overlay.py',ROOT/'tools/verify_pride_soft_tree.py',ROOT/'tools/verify_windows.py',ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,events=events,native_fields_compared=len(fields(b)),
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.profile,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
