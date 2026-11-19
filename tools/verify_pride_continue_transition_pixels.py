"""Check native-art fade pixels and neutral guest/audio preservation."""
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-continue-transition-pad-probe';out=base/'pixel-checks';out.mkdir()
    reference=base/'capture/report.json';report=bound(reference);assert report['result']=='PROTOTYPE_PASS'
    previous=ROOT/'build/pride-continue-bank-ready-probe/capture'
    commands=[]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for age in (332,600):
        folder=out/str(age);folder.mkdir();cmd=report['commands'][0].copy()
        cmd[cmd.index('--frames')+1]=str(3894+age)
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1]=str(folder/filename)
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_CONTINUE_BANK_RECORD=str(previous/'boot/bank.record'),
            TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_CONTINUE_TRANSITION='1',
            TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                creationflags=subprocess.CREATE_NO_WINDOW)
        commands.append(cmd)
    checks=dict(neutral_guest_unchanged=hashes(out/'600/run.log')==hashes(previous/'warm/run.log'),
        neutral_final_window_unchanged=pixels(out/'600/window.png')==pixels(previous/'warm/window.png'),
        neutral_pcm_unchanged=digest(out/'600/audio.wav')==digest(previous/'warm/audio.wav'))
    w,h,source=pixels(out/'332/window.png')
    for age,loss in [(333,4),(350,27)]:
        rw,rh,actual=pixels(base/f'capture/{age}/window.png')
        expected=[]
        for colour in source:
            channels=[]
            for c in colour:
                c=max(0,(c>>3)-loss);channels.append(c*8+(c>>2))
            expected.append(tuple(channels))
        checks[f'{age}/entire_native_canvas_fades']=rw==w and rh==h and actual==expected
    checks['menu_ui_preserved']=pixels(base/'capture/300/window.png')[2][:512*192]==source[:512*192]
    paths=[Path(__file__),reference,previous/'report.json']
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        public_player_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()
