"""Deterministic cold-load/restart checks and complete normal/LLE audio comparisons."""
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_soft_tree import latest
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-restart-difficulty25';bound(base/'build-report.json')
    source=ROOT/'build/pride-restart-difficulty-fixtures/report.json';fixtures=bound(source)
    out=base/'replay';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(case,label,lle=False,baseline=False):
        folder=out/(case+'-'+label);folder.mkdir();cmd=fixtures['commands'][case].copy()
        cmd[0]=str(ROOT/'build/pride-restart-difficulty24/player.exe' if baseline else base/'player.exe')
        if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,value in [('--config',out/'host.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        cmd+=['--load',str(source.parent/case/'saved.state'),'--practice-level','0','--save-at','2000',str(folder/'saved.state')]
        if lle:cmd.append('--lle')
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1',TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl')),
            stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        row=latest(folder/'tree.jsonl');commands[folder.name]=cmd;observations[folder.name]=row
        expected={'easy':0,'normal':1,'difficult':2}[case.split('-')[1]]
        checks[folder.name+'_exit']=r.returncode==0
        checks[folder.name+'_pride']=row['descriptor']==0xc00387 and row['level']==0
        checks[folder.name+'_difficulty']=row['difficulty']==expected
        checks[folder.name+'_budget']=row['lives']=={0:8,1:2,2:0}[expected] and row['health']==4
        checks[folder.name+'_save']=(folder/'saved.state').exists()
        print(folder.name,r.returncode,row['difficulty'],row['lives'],flush=True);return folder
    def same(label,a,b):
        checks[label+'_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[label+'_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')
    for nav in ('snes','md'):
        for name in ('easy','normal','difficult'):
            case=nav+'-'+name;normal=run(case,'normal');lle=run(case,'lle',lle=True);same(case+'_lle',lle,normal)
            if name=='easy':same(case+'_old_helper',run(case,'old',baseline=True),normal)
    paths=[Path(__file__),source,base/'build-report.json',ROOT/'build/pride-restart-difficulty24/build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
