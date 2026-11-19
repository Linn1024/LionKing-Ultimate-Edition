"""Check real-owner guards, old data rejection, and state-source validation."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token47';out=base/'guards';out.mkdir()
    owners=ROOT/'build/pride-effect-coverage/sun-owners2/report.json';assert bound(owners)['result']=='PASS'
    runtime=base/'artwork-verification/report.json';verified=bound(runtime);assert verified['result']=='PASS'
    source=ROOT/'tools/pride_continue_token_guard_test.c';header=ROOT/'engine/runner/tlk_continue_token_role.h'
    exe=out/'guard.exe';compile_cmd=['C:/mingw32/bin/gcc.exe','-std=c11','-O2','-Wall','-Wextra','-I'+str(header.parent),str(source),'-o',str(exe)]
    subprocess.run(compile_cmd,check=True,capture_output=True)
    captures=[owners.parent/f'sun{i}-wram.bin' for i in range(4)]
    result=subprocess.run([str(exe),*map(str,captures)],capture_output=True,text=True)
    (out/'guard.log').write_text(result.stdout+result.stderr)
    stats=json.loads(result.stdout);checks={'actual_owner_and_negative_controls':result.returncode==0 and stats['checks']==92 and stats['failures']==0}
    commands={};clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for label,choice in [('gameplay','gameplay.levels.pride_lands.porcupine_attack = snes'),('audio','audio.effects.world.life_bug = snes'),('old-package',None)]:
        folder=out/label;folder.mkdir();cmd=verified['commands']['both'].copy()
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        if choice:
            with (folder/'resources.ini').open('a') as f:f.write('\n'+choice+'\n')
        else:cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/pride-sprite-assets/sprites.assets')
        for flag in ('--dump-window','--dump-scene','--wav'):
            cmd[cmd.index(flag)+1]=str(folder/Path(cmd[cmd.index(flag)+1]).name)
        commands[label]=cmd
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        text=(folder/'run.log').read_text()
        expected='Installed sprite data is missing or incompatible.' if choice is None else 'Final scene save is invalid or source choices differ'
        checks[label+'_rejected_before_play']=rc==8 and expected in text and 'frame_sha256=' not in text and not (folder/'window.png').exists()
    paths=[Path(__file__),source,header,owners,runtime,*captures]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,guard_stats=stats,commands=commands,compile=compile_cmd,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,stats,flush=True)


if __name__=='__main__':main()
