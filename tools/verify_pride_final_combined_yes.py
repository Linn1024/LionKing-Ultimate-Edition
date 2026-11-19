"""Verify combined-source Continue YES and a post-reload cold save."""
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-final-combined';build=base/'build-report.json';bound(build)
    source=base/'lifecycle/report.json';previous=bound(source)
    out=base/'yes';out.mkdir();commands={};checks={}
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',TLK_FINAL_SCENE_PRESENT='1',
        TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    for name in ('direct','resumed'):
        folder=out/name;folder.mkdir();cmd=previous['commands']['prior-revival-to-final-menu'].copy()
        i=cmd.index('--save-at');del cmd[i:i+3];cmd[cmd.index('--frames')+1]='5300'
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
        if name=='direct':cmd+=['--save-at','5000',str(folder/'saved.state')]
        else:cmd+=['--load',str(out/'direct/saved.state')]
        with (folder/'run.log').open('wb') as log:p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        commands[name]=cmd;checks[name+'_exit']=p.returncode==0
        if name=='direct':
            checks['post_reload_save_exists']=(folder/'saved.state').is_file()
            if not checks['post_reload_save_exists']:break
    if checks.get('resumed_exit'):
        direct=out/'direct';resumed=out/'resumed'
        guest=json.loads((direct/'scene.json').read_text())['latched_gameplay']
        checks['yes_restores_playable_pride']=guest['descriptor']==0x387 and guest['health']>0 and guest['lives']==2
        checks['cold_guest']=hashes(resumed/'run.log')==hashes(direct/'run.log')
        checks['cold_client']=pixels(resumed/'window.png')==pixels(direct/'window.png')
        audio=pcm(resumed/'audio.wav');checks['cold_pcm']=bool(audio) and audio==pcm(direct/'audio.wav')[-len(audio):]
    paths=[Path(__file__),build,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
