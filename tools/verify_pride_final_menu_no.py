"""Check the installed-art NO fade against original MD, excluding credit count."""
import json
import argparse
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
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-final-menu-player9');args=parser.parse_args()
    base=ROOT/args.player;build=base/'build-report.json';bound(build)
    old_path=ROOT/'build/pride-final-menu-player2/continue/report.json';old=bound(old_path)
    ref=ROOT/'build/pride-title-exit-fade-reference/report.json';bound(ref)
    out=base/'no';out.mkdir();checks={};commands={};frames={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};env['TLK_FINAL_MD_ART']='1'
    def run(label,age,load=None):
        folder=out/label;folder.mkdir();cmd=old['commands']['320-160'].copy();cmd[0]=str(base/'player.exe')
        for flag,value in [('--config',out/'host.ini'),('--frames',3894+age),('--dump-window',folder/'window.png'),
            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if age==150:cmd+=['--save-at','4044',str(folder/'saved.state')]
        if load:cmd[cmd.index('--load')+1]=str(load/'saved.state')
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        commands[label]=cmd;checks[label+'_exit']=r.returncode==0;return folder
    levels=[[0,32,65,98,139,172,205,238],[0,32,68,101,137,170,206,238],[0,32,65,98,139,172,205,238]]
    for age in (140,141,150,151,159,160):
        folder=run(str(age),age);frames[age]=folder
        w,h,actual=pixels(folder/'window.png');rw,rh,gold=pixels(ref.parent/'no'/f'{age}.png')
        wrong=0
        for y in range(448):
            for x in range(640):
                sx=x//2;sy=y//2
                # This native gameplay fixture has one credit; the independent
                # original MD reference has three. Do not edit either counter.
                if 256<=sx<280 and 186<=sy<214:continue
                rgb=[]
                for c,value in enumerate(gold[sy*320+sx]):
                    v=levels[c].index(value);v=v*4+(v>>2);rgb.append(v<<3|v>>2)
                wrong+=actual[y*640+x]!=tuple(rgb)
        checks[str(age)+'_original_outside_counter']=not wrong
    cold=run('cold151',151,load=frames[150])
    checks['cold_guest']=hashes(cold/'run.log')==hashes(frames[151]/'run.log')
    checks['cold_client']=pixels(cold/'window.png')==pixels(frames[151]/'window.png')
    checks['cold_pcm']=pcm(cold/'audio.wav')==pcm(frames[151]/'audio.wav')[len(pcm(frames[150]/'audio.wav')):]
    paths=[Path(__file__),build,old_path,ref]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        excluded_original_comparison_rectangle=[256,186,24,28],credit_counts=[1,3],
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
