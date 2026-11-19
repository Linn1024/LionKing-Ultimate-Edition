"""Verify original pad-read counts without changing per-display-field input."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from capture_pride_ledge_physics import PATTERN
from pride_bounce_owner_preview_history import bound


def main():
    observer=ROOT/'build/pride-bounce-owner-work/player/actor-observer2'
    bp=observer/'build-report.json';assert digest(observer/'player.exe')==bound(bp)['binary_sha256']
    out=ROOT/'build/pride-ledge-controlled/poll-observer';out.mkdir()
    fixtures={
        'first':(ROOT/'build/pride-ledge-physics/snes',1472,('neutral','up','down','roll')),
        'cutscene':(ROOT/'build/pride-ledge-controlled/opposite/snes',4032,('neutral',)),
        'playable-opposite':(ROOT/'build/pride-ledge-controlled/playable-opposite/snes',2165,('neutral','up','down','roll')),
    }
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    checks={};observations={};commands={};paths=[Path(__file__),bp]
    for name,(base,point,cases) in fixtures.items():
        observations[name]={}
        for case in cases:
            per_mode=[]
            for mode in ('lle','aot'):
                label=f'{name}-{case}-{mode}';folder=out/label;folder.mkdir()
                control=base/(case+'-public' if name=='first' else case+'-public-'+mode)/'run.log'
                command=list(map(str,[observer/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                    '--md-rom',out/'absent.md','--config',base/'host.ini','--resource-profile',base/'native.ini',
                    '--load',base/'ledge.state','--input',base/(case+'.tape'),'--frames',point+120,
                    '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(point+1,point+121)))]))
                if mode=='lle':command+=['--lle']
                env=dict(clean,TLK_ACTOR_FIELDS=str(folder/'actor.csv'));commands[label]=command
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
                expected=re.findall(PATTERN,control.read_text());actual=re.findall(PATTERN,(folder/'run.log').read_text())
                checks[label+'/all_guest_fields']=len(actual)==120 and actual==expected
                rows=list(csv.DictReader((folder/'actor.csv').open()))
                checks[label+'/all_rows']=len(rows)==120
                per_mode.append(rows);paths += [control,base/'ledge.state',base/(case+'.tape')]
                print(label,'polls',sum(int(r['polls']) for r in rows),'native hashes',checks[label+'/all_guest_fields'],flush=True)
            checks[name+'/'+case+'/mode_exact_rows']=per_mode[0]==per_mode[1]
            observations[name][case]=dict(polls=sum(int(r['polls']) for r in per_mode[0]),
                no_poll_relative_fields=[i+1 for i,r in enumerate(per_mode[0]) if r['polls']=='0'],
                scene_changes=[dict(relative_field=i+1,scene=r['scene'],level=r['level']) for i,r in enumerate(per_mode[0])
                    if i==0 or r['scene']!=per_mode[0][i-1]['scene']])
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
        original_actor_observer_per_field_poll_column_is_uninstrumented=True,
        guest_writes_added=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
