"""Preserve the original-qualified navigation suite after source/restart integration."""
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
    base=ROOT/'build/pride-title-navigation23';bound(base/'build-report.json')
    source=ROOT/'build/pride-title-navigation21/verification/report.json';old=bound(source)
    out=base/'verification';out.mkdir();checks={};commands={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    labels=[label for label in old['commands'] if '-previous-' not in label and '-saved' not in label and '-cold' not in label and '-lle' not in label and not label.endswith('source-mismatch')]
    labels += [str(w)+'-'+label+'-lle' for w in (256,320) for label in ('both-directions','selected-repeat525')]
    labels += [str(w)+'-'+label+'-cold523' for w in (256,320) for label in ('selected-repeat524','selected-repeat525','held-start-into-ready','both-then-up524','both-then-down525')]
    for label in labels:
        folder=out/label;folder.mkdir();cmd=old['commands'][label].copy();cmd[0]=str(base/'player.exe')
        if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,value in [('--config',out/'host.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1'),stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        reference=source.parent/label;checks[label+'_exit']=r.returncode==0;commands[label]=cmd
        checks[label+'_client']=pixels(folder/'window.png')==pixels(reference/'window.png')
        checks[label+'_guest']=hashes(folder/'run.log')==hashes(reference/'run.log')
        checks[label+'_pcm']=pcm(folder/'audio.wav')==pcm(reference/'audio.wav')
        print(label,r.returncode,flush=True)
    paths=[Path(__file__),base/'build-report.json',source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
