"""Check observable arena revival timing, checkpoint return and real windows."""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-arena-revival-verified';out.mkdir()
    base=ROOT/'build/pride-arena-revival-probe2';route=base/'checkpoint-early'
    binary=base/'observer.exe';state=route/'during.state';identity=digest(state)
    events=list(csv.DictReader((route/'owner-events.csv').open()))
    rows=list(csv.DictReader((route/'owner-fields.csv').open()))
    by_age={int(r['age']):r for r in rows}
    scenery=json.loads((route/'scenery-evidence.json').read_text())
    checks=dict(arena_entry=scenery['latched_gameplay']['descriptor']==0x80d,
        actual_arena_recipe=scenery['stage_detected'] and scenery['camera']==[1316,198],
        begin_at_fatal=any(r['event']=='begin' and r['field']=='4430' for r in events),
        native_health_held_to_270=all(int(r['native_health'])==0 for r in rows if int(r['age'])<270),
        selected_health_at_270=int(by_age[270]['native_health'])==6,
        normal_at_345=any(r['event']=='normal' and r['age']=='345' and r['field']=='4775' for r in events))
    original_path=ROOT/'build/pride-health-death-original/report.json'
    original=json.loads(original_path.read_text())
    checks['original_md_health_delay']=original['result']=='PASS' and original['revival_health_frame']-original['death_frame']==270
    music=[int(r['frame']) for r in original['music_calls'] if r['value']=='137']
    checks['original_md_normal_delay']=music==[original['death_frame']+345]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    observations=[];commands=[]
    for field in (4454,4655,4679,4700,4775,4778):
        folder=out/str(field);folder.mkdir()
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',route/'host.ini','--resource-profile',route/'resources.ini',
             '--input-polled',ROOT/'build/pride-checkpoint-revival/snes/revival.polled.tape',
             '--load',state,'--frames',field,'--no-pace','--no-audio','--no-record',
             '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
        commands.append(list(map(str,cmd)))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        scene=json.loads((folder/'scene.json').read_text())
        observations.append(dict(field=field,gameplay=scene['latched_gameplay']))
        checks[f'{field}/no_recreated_caption']=not any(p.get('title_owner') for p in scene['pieces'])
        if field>=4775:
            game=scene['latched_gameplay']
            checks[f'{field}/checkpoint_restored']=game['player']==[1200,111] and game['health']==6 and game['lives']==7
        print(field,'actual Windows capture',flush=True)
    checks['save_unchanged']=digest(state)==identity
    paths=[Path(__file__),base/'report.json',binary,state,original_path,route/'owner-fields.csv',route/'owner-events.csv',route/'scenery-evidence.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                public_player_changed=False,all_graphics_audio_combinations_verified=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'arena revival checks',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
