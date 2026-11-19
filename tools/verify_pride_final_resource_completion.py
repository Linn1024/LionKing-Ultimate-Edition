"""Retain the supported full Pride route with the new final source both ways."""
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
    base=ROOT/'build/pride-final-resource2';out=base/'completion';out.mkdir();checks={};commands={}
    build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-arena-work/completion/report.json';previous=bound(source)
    old=source.parent;template=previous['command'];profile=Path(template[template.index('--resource-profile')+1])
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for mode in ('snes','md'):
        folder=out/mode;folder.mkdir();choice=folder/'resources.ini'
        choice.write_text(profile.read_text()+'\ngameplay.levels.pride_lands.final_life = '+mode+'\n')
        cmd=template.copy();cmd[0]=str(base/'player.exe');cmd[cmd.index('--resource-profile')+1]=str(choice)
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        commands[mode]=cmd;scene=json.loads((folder/'scene.json').read_text())
        checks[mode+'_reaches_next_level']=scene['level']==1
        checks[mode+'_guest']=hashes(folder/'run.log')==hashes(old/'run.log')
        checks[mode+'_client']=pixels(folder/'window.png')==pixels(old/'window.png')
        checks[mode+'_pcm']=pcm(folder/'audio.wav')==pcm(old/'audio.wav')
    paths=[Path(__file__),build,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
