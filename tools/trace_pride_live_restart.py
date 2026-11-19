"""Hash every native field/WRAM through the reproduced live restart route."""
import json
from pathlib import Path
import re
import subprocess
import time

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment, read_rows
from verify_windows import USER32, window_for


def main():
    prior_path=ROOT/'build/pride-practice-live/native/report.json'; prior=bound(prior_path)
    out=ROOT/'build/pride-practice-live/native-diagnostic';out.mkdir(exist_ok=True)
    assert not (out/'report.json').exists()
    folder=out/'live';folder.mkdir(exist_ok=True)
    command=list(prior['commands']['live']);binary=Path(command[0]);assert digest(binary)==prior['binary_sha256']
    config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n');command[command.index('--config')+1]=str(config)
    for flag,name in (('--dump-window','window.png'),('--dump-png','guest.png'),('--wav','audio.wav')):
        command[command.index(flag)+1]=str(folder/name)
    command+=['--hash-at',','.join(map(str,range(1,3001)))]
    env=environment(folder)
    # Keep native presentation for this diagnostic. The same guest coordinator
    # remains active. A native mismatch here cannot be repaired by hiding a
    # differing first frame in the private mixed compositor.
    env['TLK_SCENE_RENDER_ENABLE']='0'
    USER32.SetProcessDPIAware();hwnd=None;until=time.monotonic()+210
    targets=[prior['revival_begins'][0]+a for a in (225,270)]
    with (folder/'run.log').open('wb') as log:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while not hwnd:
                hwnd=window_for(proc.pid);assert proc.poll() is None and time.monotonic()<until;time.sleep(.005)
            for index,target in enumerate(targets):
                while True:
                    rows=read_rows(folder/'practice-fields.csv')
                    if rows and int(rows[-1]['field'])>=target:break
                    assert proc.poll() is None and time.monotonic()<until;time.sleep(.003)
                assert USER32.PostMessageW(hwnd,0x100,120,1);assert USER32.PostMessageW(hwnd,0x101,120,0xc0000001)
                while len(read_rows(folder/'live-load.csv'))<index+1:
                    assert proc.poll() is None and time.monotonic()<until;time.sleep(.003)
                assert read_rows(folder/'live-load.csv')[-1]['success']=='1'
            code=proc.wait(timeout=150)
        finally:
            if proc.poll() is None:
                USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    data=[(int(n),frame,ram) for n,frame,ram in re.findall(pattern,(folder/'run.log').read_text())]
    segments=[[]]
    for row in data:
        if segments[-1] and row[0]<=segments[-1][-1][0]:segments.append([])
        segments[-1].append(row)
    assert len(segments)==3 and all(segments),[len(s) for s in segments]
    reference={r[0]:r[1:] for r in segments[0]};differences=[]
    for index,segment in enumerate(segments[1:],1):
        mismatch=[dict(field=n,frame_diff=frame!=reference[n][0],ram_diff=ram!=reference[n][1])
                  for n,frame,ram in segment if n in reference and (frame,ram)!=reference[n]]
        differences.append(dict(replay=index,compared=sum(r[0] in reference for r in segment),differences=mismatch))
    paths=(Path(__file__),prior_path,ROOT/'tools/verify_pride_live_error_ui.py')
    report=dict(result='OBSERVED',exit_code=code,segments=[len(s) for s in segments],comparisons=differences,
        loads=read_rows(folder/'live-load.csv'),binary_sha256=digest(binary),command=command,
        source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        artifacts_sha256={str(q.relative_to(out)).replace('\\','/'):digest(q) for q in out.rglob('*') if q.is_file() and q.name!='report.json'},
        private_mixed_renderer_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('native diagnostic exit',code,'segments',report['segments'],'mismatches',[(r['replay'],len(r['differences']),r['differences'][:3]) for r in differences],flush=True)


if __name__=='__main__':main()
