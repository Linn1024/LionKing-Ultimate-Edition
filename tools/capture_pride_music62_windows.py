"""Capture the candidate's real Windows victory using its own current save."""
import json
import os
from pathlib import Path
import re
import subprocess
import time
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import USER32,window_for
from verify_pride_soft_tree import latest
from windows_capture import capture_client


def main():
    source=ROOT/'build/pride-music-output62/verification/resume-qualification/report.json';prior=bound(source);assert prior['result']=='PASS'
    bp=ROOT/'build/pride-music-output62/build-report.json';build=bound(bp)
    out=bp.parent/'windows';out.mkdir();cmd=prior['commands']['music-aot'].copy();cmd.remove('--no-pace')
    cmd[cmd.index('--frames')+1]='4620';i=cmd.index('--dump-window');del cmd[i:i+2]
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
    for flag,file in [('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env['TLK_SOFT_TREE_LOG']=str(out/'tree.jsonl');USER32.SetProcessDPIAware();checks={};hwnd=None
    with (out/'run.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline=time.monotonic()+90
            while proc.poll() is None and time.monotonic()<deadline:
                row=latest(out/'tree.jsonl')
                if row and row['field']>=4598:
                    hwnd=window_for(proc.pid)
                    if hwnd:break
                time.sleep(.003)
            assert hwnd,('owned victory window missing',latest(out/'tree.jsonl'))
            before=latest(out/'tree.jsonl');capture_client(hwnd,out/'victory.png');after=latest(out/'tree.jsonl')
            checks['victory_interval']=4598<=before['field']<=after['field']<=4620
            checks['difficult_alive_in_arena']=before['difficulty']==2 and before['health']==2 and before['descriptor']==0xc0080d
            checks['md_music_selected']=next(c[-1] for c in before['choices'] if c[0]=='audio.music.pride_lands')==2
            proc.wait(timeout=30);checks['clean_exit']=proc.returncode==0
        finally:
            if proc.poll() is None:
                if hwnd:USER32.PostMessageW(hwnd,0x10,0,0)
                try:proc.wait(timeout=10)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=5)
    scene=json.loads((out/'scene.json').read_text())
    checks['owned_dead_boss']=any(p['actor_descriptor']==0xc58c68 and p['actor_owner']==p['object'] and p['actor_action']==0xc147f7 for p in scene['pieces'])
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    actual=re.findall(pattern,(out/'run.log').read_text());expected=re.findall(pattern,(bp.parent/'verification/music-aot/run.log').read_text())
    checks['all600_fight_guest_fields_exact']=len(actual)==600 and actual==[r for r in expected if int(r[0])>4000]
    checks['binary_exact']=digest(Path(cmd[0]))==build['binary_sha256']
    paths=[Path(__file__),source,bp,ROOT/'tools/windows_capture.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,before=before,after=after,
                actual_owned_os_capture=True,device_audio_tested=False,current_build_save_only=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
