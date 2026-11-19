"""Compare maintained compiled/LLE title routes with the original-qualified probe."""
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
    base=ROOT/'build/pride-title-ready18';bound(base/'build-report.json')
    source=ROOT/'build/pride-title-readiness-probe3/contexts/report.json';old=bound(source)
    out=base/'contexts';out.mkdir();checks={};commands={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(key,label,end=None,save=False,load=None,lle=False):
        folder=out/(key.replace('/','-')+'-'+label);folder.mkdir()
        cmd=old['commands'][key].copy();cmd[0]=str(base/'player.exe');cmd.remove('--lle')
        if lle:cmd.append('--lle')
        if end is not None:cmd[cmd.index('--frames')+1]=str(end)
        for flag,value in [('--config',out/'host.ini'),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if save:cmd+=['--save-at',cmd[cmd.index('--frames')+1],str(folder/'saved.state')]
        if load:cmd[cmd.index('--load')+1]=str(load)
        env=dict(clean,TLK_FINAL_MD_ART='1')
        if key.startswith('continue-'):env['TLK_CONTINUE_BANK_RECORD']=str(ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record')
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[folder.name]=cmd;checks[folder.name+'_exit']=r.returncode==0
        print(folder.name,r.returncode,flush=True);return folder
    def same(label,a,b,skip=0):
        checks[label+'_client']=(a/'window.png').exists() and pixels(a/'window.png')==pixels(b/'window.png')
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[label+'_pcm']=(a/'audio.wav').exists() and pcm(a/'audio.wav')==pcm(b/'audio.wav')[skip:]
    for key in old['commands']:
        normal=run(key,'normal')
        same(key+'_probe',normal,source.parent/key)
        other=run(key,'lle',lle=True);same(key+'_lle',other,normal)
        case,label=key.split('/')
        if label in ('start','held'):
            ready=old['observations'][case]['ready'];origin=3894 if case.startswith('continue-') else 4444
            before=run(key,'saved',end=origin+ready-1,save=True)
            cold=run(key,'cold',load=before/'saved.state')
            same(key+'_cold',cold,normal,len(pcm(before/'audio.wav')))
    paths=[Path(__file__),base/'build-report.json',source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,binary_sha256=digest(base/'player.exe'),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
