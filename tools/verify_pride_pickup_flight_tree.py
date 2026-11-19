"""Apply independent pickup artwork/palette overrides in the real paused resource tree."""
import json
import os
import re
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_soft_tree import latest
from verify_pride_audio_state import wav_data
from verify_windows import USER32,window_for,hashes
from windows_capture import capture_client


def main():
    base=ROOT/'build/pride-flight-player';bp=base/'build-report.json';bound(bp)
    out=base/'flight-tree';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 3\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape';checks={};commands={};snapshots={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for name in ('control','live'):
        folder=out/name;folder.mkdir();profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
        trace=folder/'tree.jsonl';env=dict(clean)
        cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profile,'--config',config,'--input-polled',tape,'--frames',1624,
            '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,1625))),
            '--wav',folder/'audio.wav','--wav-seconds',60,'--dump-png',folder/'guest.png']
        if name=='live':
            cmd+=['--menu-at',1616,'--menu-page','resources'];env['TLK_SOFT_TREE_LOG']=str(trace)
        commands[name]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            if name=='control':
                subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
                continue
            process=subprocess.Popen(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                def wait(predicate):
                    deadline=time.monotonic()+90
                    while time.monotonic()<deadline and process.poll() is None:
                        row=latest(trace)
                        if row and predicate(row):return row
                        time.sleep(.02)
                    raise AssertionError(('UI timeout',process.poll(),latest(trace)))
                wait(lambda r:r['menu']==1 and r['about']==2)
                hwnd=window_for(process.pid);assert hwnd
                USER32.SetProcessDPIAware()
                def key(value):
                    scan=USER32.MapVirtualKeyW(value,0);extra=0x1000000 if 0x21<=value<=0x28 else 0
                    assert USER32.PostMessageW(hwnd,0x100,value,1+(scan<<16)+extra)
                    assert USER32.PostMessageW(hwnd,0x101,value,0xc0000001+(scan<<16)+extra)
                    time.sleep(.06)
                def choice(row,node):return next(c for c in row['choices'] if c[0]==node)
                def select(node):
                    key(0x24)
                    for _ in range(150):
                        row=latest(trace);selected=row['choices'][row['selected']][0]
                        if selected==node:return
                        if node.startswith(selected+'.') or selected=='game':key(0x27)
                        key(0x28)
                    raise AssertionError(('Missing pickup node',node))
                def setchoice(node,value):
                    select(node)
                    for _ in range(3):
                        if choice(latest(trace),node)[1]==value:return
                        key(0x0d)
                    wait(lambda r:choice(r,node)[1]==value)
                def apply(label):
                    key(0x71);wait(lambda r:r['modal']==1);key(0x1b)
                    row=wait(lambda r:r['dirty']==0)
                    snapshots[label]=row;capture_client(hwnd,folder/(label+'.png'))
                    return row
                branch='graphics.sprites.pickups'
                initial=profile.read_bytes()
                setchoice(branch,2);setchoice(branch+'.palette',1)
                checks['draft_does_not_publish']=profile.read_bytes()==initial
                row=apply('md-frames-native-palette')
                checks['independent_frame_source']=choice(row,branch+'.frames')[4]==2 and choice(row,branch+'.palette')[4]==1
                setchoice(branch+'.frames',1);setchoice(branch+'.palette',2)
                row=apply('native-frames-md-palette')
                checks['independent_palette_source']=choice(row,branch+'.frames')[4]==1 and choice(row,branch+'.palette')[4]==2
                setchoice(branch,1);setchoice(branch+'.frames',0);setchoice(branch+'.palette',0)
                row=apply('native-restored')
                checks['native_inheritance_restored']=choice(row,branch+'.frames')[4]==1 and choice(row,branch+'.palette')[4]==1
                checks['no_level_restart_or_advance']=all(r['field']==1616 for r in snapshots.values())
                checks['choices_persist']='graphics.sprites.pickups = snes' in profile.read_text()
                key(0x1b);key(0x1b);key(0x1b)
                process.wait(timeout=120);assert process.returncode==0
            finally:
                if process.poll() is None:process.terminate();process.wait(timeout=5)
    a,b=out/'control',out/'live'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    checks['every_guest_picture_full_wram_field']=len(rows(a))==1624 and rows(a)==rows(b)
    checks['entire_pcm_unchanged']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
    checks['final_guest_hashes']=hashes(a/'run.log')==hashes(b/'run.log')
    paths=[__file__,bp,ROOT/'tools/verify_pride_soft_tree.py',ROOT/'tools/windows_capture.py']
    from pathlib import Path
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,snapshots=snapshots,
        compared_fields=1624,source_sha256={Path(p).resolve().relative_to(ROOT).as_posix():digest(Path(p)) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'real resource-tree checks',flush=True);assert all(checks.values())


if __name__=='__main__':main()
