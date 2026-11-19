"""Read-only poll-position evidence for adapting the existing ordinary route prefix."""
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
    base=ROOT/'build/pride-restart-prefix-observer26';build=bound(base/'build-report.json')
    source=ROOT/'build/pride-restart-difficulty25/completion/report.json';old=bound(source)
    out=base/'capture';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for nav in ('snes','md'):
        folders=[]
        for observed in (False,True):
            label=nav+('-observer' if observed else '-maintained');folder=out/label;folder.mkdir();folders.append(folder)
            cmd=old['commands'][f'256-{nav}'].copy()
            if observed:cmd[0]=str(base/'player.exe')
            for flag,value in [('--frames',1200),('--config',out/'host.ini'),('--dump-window',folder/'window.png'),
                               ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
            with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_FINAL_MD_ART='1',TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl')),
                stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
            commands[label]=cmd;checks[label+'_exit']=r.returncode==0
            rows=[json.loads(line) for line in (folder/'tree.jsonl').read_text().splitlines()]
            observations[label]=[{k:row.get(k) for k in ('field','level','descriptor','difficulty','lives','poll_index')} for row in rows if 500<=row['field']<=850]
        a,b=folders
        checks[nav+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[nav+'_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[nav+'_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')
    paths=[Path(__file__),base/'build-report.json',source]
    report=dict(result='NEUTRAL' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                binary_sha256=build['binary_sha256'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
