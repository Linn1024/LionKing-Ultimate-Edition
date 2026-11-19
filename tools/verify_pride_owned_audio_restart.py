"""Apply the arrival audio leaf in the real tree and verify genuine cold restarts."""
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_history import bound
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import read_rows
from verify_pride_soft_tree import latest
from verify_pride_source_controls import macro_tape
from verify_windows import USER32,window_for,pixels
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-bounce-owner-work/player';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    out=base/'bounce-restart';out.mkdir();checks={};commands={};snapshots={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    node='audio.effects.simba.bounce'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for label,initial,target,mode in (('to-md',1,2,'aot'),('to-native',2,1,'lle')):
        folder=out/label;folder.mkdir();live=folder/'live';live.mkdir();cold=folder/'cold';cold.mkdir()
        config=live/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        profile=live/'resources.ini';profile.write_text('schema = 1\ngame = snes\n'+node+' = '+('md' if initial==2 else 'snes')+'\n')
        trace=live/'tree.jsonl';env=dict(clean,TLK_SOFT_TREE_LOG=str(trace),TLK_PRIDE_DIAGNOSTICS=str(live))
        command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--resource-profile',profile,
            '--practice-level',0,'--frames',1800,'--menu-at',1500,'--menu-page','resources',
            '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,1801))),
            '--wav',live/'audio.wav','--wav-seconds',100,'--dump-png',live/'guest.png']))
        if mode=='lle':command+=['--lle']
        commands[label+'/live']=command
        with (live/'run.log').open('wb') as log:
            proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                def wait(predicate):
                    deadline=time.monotonic()+120
                    while time.monotonic()<deadline:
                        row=latest(trace)
                        if row and predicate(row):return row
                        if proc.poll() is not None:break
                        time.sleep(.02)
                    raise AssertionError(('menu timeout',proc.poll(),latest(trace)))
                wait(lambda r:r['menu']==1 and r['about']==2)
                hwnd=window_for(proc.pid);assert hwnd;USER32.SetProcessDPIAware()
                def key(value):
                    scan=USER32.MapVirtualKeyW(value,0);extra=0x1000000 if 0x21<=value<=0x28 else 0
                    assert USER32.PostMessageW(hwnd,0x100,value,1+(scan<<16)+extra)
                    assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001+(scan<<16)+extra)
                    time.sleep(.06)
                key(0x24)
                for _ in range(150):
                    row=latest(trace);selected=row['choices'][row['selected']][0]
                    if selected==node:break
                    if node.startswith(selected+'.') or selected=='game':key(0x27)
                    key(0x28)
                else:raise AssertionError('arrival leaf missing')
                original=profile.read_bytes()
                for _ in range(3):
                    choice=next(c for c in latest(trace)['choices'] if c[0]==node)
                    if choice[1]==target:break
                    key(0x0d)
                row=latest(trace);snapshots[label+'/draft']=row
                checks[label+'/draft_preserves_profile']=profile.read_bytes()==original and row['dirty']==1 and row['field']==1500
                capture_client(hwnd,live/'pending.png')
                key(0x71)
                row=wait(lambda r:r['menu']==0 and r['dirty']==0)
                snapshots[label+'/applied']=row
                checks[label+'/persisted_and_active']=node+' = '+('md' if target==2 else 'snes') in profile.read_text() and next(c for c in row['choices'] if c[0]==node)[4]==target
                capture_client(hwnd,live/'restarted.png')
                proc.wait(timeout=180);assert proc.returncode==0
            finally:
                if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        loads=read_rows(live/'live-load.csv')
        checks[label+'/genuine_field_zero_restart']=len(loads)==2 and all(r['success']=='1' and r['loaded_field']=='0' for r in loads) and loads[-1]['attempt_field']=='1500'
        boot=live/'tlk_practice_boot.state';header=boot.read_bytes()[:16]
        assert header[:8]==b'TLKSTAT1' and struct.unpack_from('<II',header,8)==(4,0)
        tape=cold/'level-select.raw';tape.write_bytes(macro_tape(bytes(6000)))
        cold_config=cold/'host.ini';cold_config.write_text('opengl = 0\nscale = 2\n')
        command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--config',cold_config,'--resource-profile',profile,
            '--load',boot,'--input-raw',tape,'--frames',1800,'--no-pace','--no-audio','--no-record',
            '--hash-at',','.join(map(str,range(1,1801))),'--wav',cold/'audio.wav','--wav-seconds',60,
            '--dump-png',cold/'guest.png','--dump-window',cold/'window.png']))
        if mode=='lle':command+=['--lle']
        commands[label+'/cold']=command
        with (cold/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        rows=lambda path:re.findall(pattern,path.read_text())
        a,b=rows(cold/'run.log'),rows(live/'run.log')
        checks[label+'/all_restarted_guest_fields']=len(a)==1800 and len(b)==3300 and a==b[-1800:]
        pcm=wav_data(cold/'audio.wav');whole=wav_data(live/'audio.wav')
        checks[label+'/whole_restarted_pcm']=bool(pcm) and len(whole)>len(pcm) and whole[-len(pcm):]==pcm
        checks[label+'/final_guest_picture']=pixels(cold/'guest.png')==pixels(live/'guest.png')
        print(label,'failed',[k for k,v in checks.items() if not v],flush=True)
    paths=[Path(__file__),bp,ROOT/'tools/verify_pride_source_controls.py',ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,snapshots=snapshots,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        compared_restart_fields=3600,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'actual source restart checks',flush=True);assert all(checks.values())


if __name__=='__main__':main()
