"""Check corrected menu positioning leaves the subsequent game unchanged."""
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
    base=ROOT/'build/pride-final-menu-player10';source=base/'layout/report.json';data=bound(source)
    reference=ROOT/'build/pride-final-menu-player9/handoff2/report.json';bound(reference)
    out=base/'handoff';out.mkdir();checks={};commands={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    bank=ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record'
    env.update(TLK_FINAL_MD_ART='1',TLK_CONTINUE_BANK_RECORD=str(bank))
    for width in (256,320):
        folders={}
        for label,age,cold in [('full',426,False),('live',600,False),('cold',600,True)]:
            folder=out/f'{width}-{label}';folder.mkdir();folders[label]=folder
            cmd=data['commands'][f'{width}-yes-197'].copy()
            for flag,value in [('--config',out/'host.ini'),('--frames',3894+age),('--dump-window',folder/'window.png'),
                ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
            if cold:cmd[cmd.index('--load')+1]=str(source.parent/f'{width}-yes-333/saved.state')
            with (folder/'run.log').open('wb') as log:
                result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
            commands[f'{width}-{label}']=cmd;checks[f'{width}-{label}_exit']=result.returncode==0
            prior=reference.parent/f'{width}-{age}'
            checks[f'{width}-{label}_gameplay_picture']=pixels(folder/'window.png')==pixels(prior/'window.png')
            checks[f'{width}-{label}_guest']=hashes(folder/'run.log')==hashes(prior/'run.log')
            if label=='live':checks[f'{width}_live_pcm']=pcm(folder/'audio.wav')==pcm(prior/'audio.wav')
            if cold:checks[f'{width}_cold_pcm']=pcm(folder/'audio.wav')==pcm(prior/'audio.wav')[len(pcm(source.parent/f'{width}-yes-333/audio.wav')):]
            print(width,label,'exit',result.returncode,flush=True)
    paths=[Path(__file__),source,reference,bank]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
