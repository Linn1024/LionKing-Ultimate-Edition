"""Observe whether current compiled execution reaches the research transfer hooks."""
import csv
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm

def main():
    source=ROOT/'build/pride-title-upload-fast5/report.json';data=bound(source)
    manifest=ROOT/'build/pride-title-bank-installed/setup-verification/Game data & title bank/install.json';info=json.loads(manifest.read_text());bank=manifest.parent/info['title_bank_assets']['file']
    out=ROOT/'build/pride-title-upload-modes5';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    for width in (256,320):
        folder=out/str(width);folder.mkdir();cmd=data['commands'][str(width)].copy();cmd.remove('--lle')
        for flag,value in [('--config',out/'host.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(TLK_FINAL_MD_ART='1',TLK_TITLE_AUDIO_DIR=str(folder),TLK_TITLE_UPLOAD_FAST='1',TLK_TITLE_UPLOAD_BANK=str(bank),TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[str(width)]=cmd;checks[f'{width}_exit']=r.returncode==0
        if r.returncode:continue
        previous=source.parent/str(width)
        checks[f'{width}_client']=pixels(folder/'window.png')==pixels(previous/'window.png')
        checks[f'{width}_guest']=hashes(folder/'run.log')==hashes(previous/'run.log')
        checks[f'{width}_pcm']=pcm(folder/'audio.wav')==pcm(previous/'audio.wav')
        copies=[r for r in csv.reader((folder/'upload.csv').open()) if r and r[0]=='copy']
        checks[f'{width}_sixteen_copies']=len(copies)==16
        first=next(int(r[1]) for r in csv.reader((folder/'exit.csv').open()) if r[0]=='frame' and r[2]=='c005ab' and int(r[5]))
        observations[str(width)]=dict(first_title=first,copies=len(copies))
        print(width,'first',first,'copies',len(copies),flush=True)
    paths=[Path(__file__),source,manifest,bank]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                scope='Research current compiled mode vsLLE; no production integration or capability claim',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)

if __name__=='__main__':main()
