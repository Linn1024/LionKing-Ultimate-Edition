"""Exercise popup source inheritance and live apply in the real Windows tree."""
import json
import os
import subprocess
import time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_soft_tree import latest
from verify_pride_audio_state import wav_data
from verify_windows import USER32,window_for,hashes
from windows_capture import capture_client

BRANCH='graphics.sprites.effects.pickup_arrival'


def main():
    base=ROOT/'build/pride-popup-work';out=base/'tree';out.mkdir()
    report_path=base/'commands4.json';build=json.loads(report_path.read_text())
    binary=base/'player/native-engine/tlk_pride_player.exe'
    assert digest(binary)==build['binary_sha256']
    checks={};snapshots={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for name in ('control','live'):
        folder=out/name;folder.mkdir()
        profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
        config=folder/'host.ini';config.write_text('opengl = 0\nscale = 3\n')
        trace=folder/'tree.jsonl'
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input-polled',ROOT/'engine/tapes/allbugsF.read.tape',
             '--frames',1672,'--no-pace','--no-audio','--no-record','--wav',folder/'audio.wav','--wav-seconds',60]
        env=dict(clean)
        if name=='live':cmd+=['--menu-at',1664,'--menu-page','resources'];env['TLK_SOFT_TREE_LOG']=str(trace)
        commands[name]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            if name=='control':
                subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,check=True)
                continue
            process=subprocess.Popen(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                def wait(predicate):
                    deadline=time.monotonic()+90
                    while time.monotonic()<deadline and process.poll() is None:
                        row=latest(trace)
                        if row and predicate(row):return row
                        time.sleep(.02)
                    raise AssertionError(('Resource tree timeout',process.poll(),latest(trace)))
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
                    for _ in range(180):
                        row=latest(trace);selected=row['choices'][row['selected']][0]
                        if selected==node:return
                        if node.startswith(selected+'.') or selected=='game':key(0x27)
                        key(0x28)
                    raise AssertionError(('Missing popup node',node))
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
                initial=profile.read_bytes()
                setchoice(BRANCH,2);setchoice(BRANCH+'.palette',1);setchoice(BRANCH+'.position',1)
                checks['draft_not_published']=profile.read_bytes()==initial
                row=apply('md-frames')
                checks['independent_frames']=[choice(row,BRANCH+'.'+n)[4] for n in ('frames','palette','position')]==[2,1,1]
                setchoice(BRANCH+'.frames',1);setchoice(BRANCH+'.palette',2);setchoice(BRANCH+'.position',2)
                row=apply('md-palette-position')
                checks['independent_palette_position']=[choice(row,BRANCH+'.'+n)[4] for n in ('frames','palette','position')]==[1,2,2]
                setchoice(BRANCH,1)
                for node in ('frames','palette','position'):setchoice(BRANCH+'.'+node,0)
                row=apply('native-restored')
                checks['native_inheritance']=[choice(row,BRANCH+'.'+n)[4] for n in ('frames','palette','position')]==[1,1,1]
                checks['live_without_level_restart']=all(r['field']==1664 for r in snapshots.values())
                checks['persisted_branch']=BRANCH+' = snes' in profile.read_text()
                key(0x1b);key(0x1b);key(0x1b)
                process.wait(timeout=120);assert process.returncode==0
            finally:
                if process.poll() is None:process.terminate();process.wait(timeout=5)
    checks['guest_state_unchanged']=hashes(out/'control/run.log')==hashes(out/'live/run.log')
    checks['entire_pcm_unchanged']=wav_data(out/'control/audio.wav')==wav_data(out/'live/audio.wav')
    paths=[Path(__file__),report_path,ROOT/'tools/windows_capture.py',ROOT/'tools/verify_pride_soft_tree.py']
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,snapshots=snapshots,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'actual resource-tree checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
