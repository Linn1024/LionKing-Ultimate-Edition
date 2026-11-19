"""Check the reduced preparation and real destination pictures in an isolated host."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels,hashes


def main():
    base=ROOT/'build/pride-final-display-probe2';out=base/'capture';out.mkdir()
    build=bound(base/'build-report.json');binary=base/'player.exe';assert digest(binary)==build['binary_sha256']
    state=ROOT/'build/pride-final-presentation/preview/prefatal.state';identity=digest(state)
    tape=ROOT/'build/pride-final-presentation/preview/ordinary.tape'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    checks={};commands=[];observations=[]
    for mode,offsets in [('control',(0,88,436)),('candidate',(0,8,96,97,98,99,100,101,102,104,120,160))]:
        for offset in offsets:
            folder=out/f'{mode}-{offset}';folder.mkdir()
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',profile,'--config',config,'--input',tape,'--load',state,'--lle','--frames',2369+offset,
                 '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
            commands.append(list(map(str,cmd)))
            env=dict(clean,TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP=str(int(mode=='candidate')))
            with (folder/'run.log').open('wb') as log:
                subprocess.run(commands[-1],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            w,h,data=pixels(folder/'window.png');scene=json.loads((folder/'scene.json').read_text())
            observations.append(dict(mode=mode,offset=offset,nonblack=sum(p!=(0,0,0) for p in data),
                peak=max(max(p) for p in data),pieces=len(scene['pieces']),poses=sorted({p['pose'] for p in scene['pieces']})))
            if mode=='control':
                reference=ROOT/'build/pride-final-presentation/preview'/str(offset)
                checks[f'control/{offset}/gameplay_preserved']=hashes(folder/'run.log')==hashes(reference/'run.log')
                checks[f'control/{offset}/window_preserved']=pixels(folder/'window.png')==pixels(reference/'window.png')
            print(mode,offset,observations[-1],flush=True)
    at={r['offset']:r for r in observations if r['mode']=='candidate'}
    checks['candidate/complete_destination_at_100']=at[100]['pieces']==29 and at[100]['nonblack']>1000
    checks['candidate/black_at_98']=at[98]['nonblack']==0
    events=list(csv.DictReader((out/'candidate-160/points.csv').open()))
    checks['candidate/preparation_waits_owned']=any(r['pc']=='c08a1a' and r['field']=='2369' for r in events)
    checks['candidate/late_bypass_preserved']=any(r['pc']=='c08a59' and r['field']=='2375' for r in events)
    checks['prefatal_save_unchanged']=digest(state)==identity
    paths=[Path(__file__),base/'build-report.json',binary,state,tape]
    report=dict(result='FEASIBILITY_ONLY' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        final_fade_renderer_implemented=False,interpreter_only_experiment=True,final_life_adapter_published=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'reduced preparation checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
