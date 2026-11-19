"""Verify accelerated Continue reload through real Windows clients and controls."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes, pixels


def main():
    base=ROOT/'build/pride-continue-fast-reload-probe'; out=base/'capture'; out.mkdir()
    build=bound(base/'build-report.json')
    assets=ROOT/'build/pride-continue-reload-assets/report.json'
    assert bound(assets)['result']=='PASS'
    prior=ROOT/'build/pride-continue-exit-observation2'; original=bound(prior/'report.json')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    observations={}; commands=[]; checks={}
    for name,enabled,moving in [('control',False,False),('fast',True,False),('moving',True,True)]:
        folder=out/name; folder.mkdir()
        cmd=original['commands'][-1].copy();cmd[0]=str(base/'player.exe')
        for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json')]:
            cmd[cmd.index(flag)+1]=str(folder/filename)
        if moving:
            raw=bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes())
            fatal=3894
            for age in range(550,601):struct.pack_into('<H',raw,(fatal+age-1)*2,0x100)
            tape=folder/'moving.tape';tape.write_bytes(raw);cmd[cmd.index('--input')+1]=str(tape)
        env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
            TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD=str(int(enabled)),
            TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
        rows=list(csv.DictReader((folder/'exit.csv').open()))
        frames=[r for r in rows if r['kind']=='frame' and int(r['age'])>124]
        black=[int(r['age']) for r in frames if r['a_or_lit']=='0']
        gameplay=json.loads((folder/'scene.json').read_text())['latched_gameplay']
        observations[name]=dict(gameplay=gameplay,fast_loads=[r for r in rows if r['kind']=='fast'],
            first_healthy=next((int(r['age']) for r in frames if 0<int(r['health'])<10),None),
            black_intervals=[(int(r['age']),r['a_or_lit']=='0') for n,r in enumerate(frames) if n and
                (r['a_or_lit']=='0')!=(frames[n-1]['a_or_lit']=='0')])
        commands.append(cmd)
        print(name,observations[name],flush=True)
    reference=prior/'native/600'
    checks['disabled_guest_unchanged']=hashes(out/'control/run.log')==hashes(reference/'run.log')
    checks['disabled_window_unchanged']=pixels(out/'control/window.png')==pixels(reference/'window.png')
    for name in ('fast','moving'):
        checks[name+'/all_nine_recipes']=len(observations[name]['fast_loads'])==9
        checks[name+'/main_pride']=observations[name]['gameplay']['descriptor']==903
        checks[name+'/health_lives']=observations[name]['gameplay']['health']==4 and observations[name]['gameplay']['lives']==2
    checks['idle_spawn_correct']=observations['fast']['gameplay']['player']==[64,1255]
    checks['right_moves_player']=observations['moving']['gameplay']['player'][0]>observations['fast']['gameplay']['player'][0]+30
    checks['reload_shorter']=observations['fast']['first_healthy']<observations['control']['first_healthy']
    paths=[Path(__file__),base/'build-report.json',assets,prior/'report.json']
    report=dict(result='PROTOTYPE_PASS' if all(checks.values()) else 'FAIL',checks=checks,
        observations=observations,commands=commands,public_player_changed=False,
        source_mixing_lifecycle_and_original_timing_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
