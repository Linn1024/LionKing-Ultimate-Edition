"""Check the accelerated reload's first visible frame in actual Windows clients."""
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-continue-bank-ready-probe';out=base/'first-view';out.mkdir()
    reference=base/'capture/report.json';report=bound(reference)
    assert report['result']=='PROTOTYPE_PASS'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    observations={};commands=[]
    for age in (401,402):
        folder=out/str(age);folder.mkdir();cmd=report['commands'][2].copy()
        cmd[cmd.index('--frames')+1]=str(3894+age)
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json')]:
            cmd[cmd.index(flag)+1]=str(folder/name)
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',
            TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_CONTINUE_BANK_APPLY='1',
            TLK_CONTINUE_BANK_DIR=str(folder),TLK_CONTINUE_BANK_RECORD=str(base/'capture/boot/bank.record'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
        w,h,data=pixels(folder/'window.png')
        observations[str(age)]=dict(width=w,height=h,lit=sum(p!=(0,0,0) for p in data))
        commands.append(cmd)
    checks=dict(black_before=observations['401']['lit']==0,
        visible_at_402=observations['402']['lit']>10000,
        real_window_size=all(r['width']==512 and r['height']==448 for r in observations.values()))
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        observations=observations,commands=commands,public_player_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),reference)},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,observations,flush=True);assert all(checks.values())


if __name__=='__main__':main()
