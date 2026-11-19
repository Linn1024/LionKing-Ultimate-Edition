"""Verify ordinary Continue NO/timeout use installed title data and cold resumes."""
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
    base=ROOT/'build/pride-title-native15';source=ROOT/'build/pride-title-native14/continue-regressions/report.json';old=bound(source)
    out=base/'contexts';out.mkdir();checks={};commands={};observed={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    def run(width,case,age,label,load=None,save=False,lle=False):
        folder=out/f'{width}-{case}-{label}';folder.mkdir()
        key=f'{width}-'+('no-150' if case=='no' else 'neutral-160')
        cmd=old['commands'][key].copy();cmd[0]=str(base/'player.exe')
        if '--save-at' in cmd:
            at=cmd.index('--save-at');del cmd[at:at+3]
        for flag,value in [('--config',out/'host.ini'),('--frames',3894+age),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        cmd+=['--wav-seconds','120']
        if load:cmd[cmd.index('--load')+1]=str(load)
        if save:cmd+=['--save-at',str(3894+age),str(folder/'saved.state')]
        if lle:cmd+=['--lle']
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(old['environments'][key]);env['TLK_CONTINUE_EXIT_LOG']=str(folder/'exit.csv')
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[folder.name]=cmd;checks[folder.name+'_exit']=r.returncode==0;print(folder.name,r.returncode,flush=True);return folder
    for width in (256,320):
        for case,saved,target,expected in [('no',220,700,251),('timeout',920,1200,956)]:
            before=run(width,case,saved,'saved',save=True)
            live=run(width,case,target,'live')
            rows=list(csv.reader((live/'exit.csv').open()));copies=[r for r in rows if r[0]=='title_fast']
            checks[f'{width}_{case}_ten_copies']=len(copies)==10 and {int(r[5]) for r in copies}==set(range(10,20))
            first=next(int(r[1]) for r in rows if r[0]=='frame' and r[2]=='c005ab' and int(r[5])>0)
            checks[f'{width}_{case}_first_picture']=first==expected
            observed[f'{width}_{case}']=dict(first_title=first,original=186 if case=='no' else 890,remaining=first-(186 if case=='no' else 890))
            cold=run(width,case,target,'cold',load=before/'saved.state')
            lle=run(width,case,target,'lle',lle=True)
            for label,folder,skip in [('cold',cold,len(pcm(before/'audio.wav'))),('lle',lle,0)]:
                checks[f'{width}_{case}_{label}_client']=pixels(folder/'window.png')==pixels(live/'window.png')
                checks[f'{width}_{case}_{label}_guest']=hashes(folder/'run.log')==hashes(live/'run.log')
                checks[f'{width}_{case}_{label}_pcm']=pcm(folder/'audio.wav')==pcm(live/'audio.wav')[skip:]
    # Old v1 data cannot silently turn installed title playback into ROM decoding.
    cmd=old['commands']['320-neutral-140'].copy();cmd[0]=str(base/'player.exe');cmd[cmd.index('--final-native-assets')+1]=str(ROOT/'build/pride-final-native-installed/native.assets')
    cmd[cmd.index('--config')+1]=str(out/'host.ini')
    # Loader must stop before it reaches the old dump paths in the template.
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    with (out/'v1.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    commands['v1_rejection']=cmd
    checks['v1_package_rejects_before_guest']=r.returncode==6 and b'loaded_state=' not in (out/'v1.log').read_bytes()
    paths=[Path(__file__),source,base/'build-report.json',ROOT/'engine/runner/pride/final/pride_final_runtime.inc']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observed,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
