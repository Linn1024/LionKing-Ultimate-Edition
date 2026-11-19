"""Check final-life selection from the resource profile without enabling flags."""
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
    base=ROOT/'build/pride-final-resource2';out=base/'verification';out.mkdir();checks={};commands={}
    build=base/'build-report.json';bound(build)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    references=[ROOT/'build/pride-final-wide/verification/report.json',
        ROOT/'build/pride-final-mixed-fade/verification/report.json']
    cases=[]
    wide=bound(references[0]);native=bound(references[1])
    for key in ('native-0','native-19','scenery-7','sprites-100','scenery-resumed0-1','sprites-resumed7-10'):
        cases.append((key,wide['commands'][key],True))
    cases.append(('native-death-final',native['commands']['palettes-resumed10'],True))
    cases.append(('native-final',wide['commands']['native-control1'],False))
    for label,template,enabled in cases:
        folder=out/label;folder.mkdir();cmd=template.copy();cmd[0]=str(base/'player.exe')
        if '--save-at' in cmd:
            i=cmd.index('--save-at');del cmd[i:i+3]
        profile=folder/'resources.ini';oldprofile=Path(cmd[cmd.index('--resource-profile')+1])
        profile.write_text(oldprofile.read_text()+'\ngameplay.levels.pride_lands.final_life = '+('md' if enabled else 'snes')+'\n')
        cmd[cmd.index('--resource-profile')+1]=str(profile)
        previous=Path(template[template.index('--dump-window')+1]).parent
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1]=str(folder/name)
        selected=dict(env,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'))
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=selected,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        commands[label]=cmd;checks[label+'_exit']=result.returncode==0
        if result.returncode:continue
        checks[label+'_guest']=hashes(folder/'run.log')==hashes(previous/'run.log')
        checks[label+'_client']=pixels(folder/'window.png')==pixels(previous/'window.png')
        checks[label+'_pcm']=pcm(folder/'audio.wav')==pcm(previous/'audio.wav')
        tree=json.loads((folder/'tree.jsonl').read_text().splitlines()[-1])
        leaf=next(c for c in tree['choices'] if c[0]=='gameplay.levels.pride_lands.final_life')
        checks[label+'_tree_choice']=leaf[-1]==(2 if enabled else 1)
    paths=[Path(__file__),build,*references]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        no_mode_environment_flags=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
