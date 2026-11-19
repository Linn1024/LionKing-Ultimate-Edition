"""Compare final-life pictures at matching scene age with neutral post-hit input."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from capture_pride_ledge_physics import PATTERN
from pride_scene_template_history import bound
from verify_windows import pixels


def main():
    out=ROOT/'build/pride-final-skip-phase';out.mkdir()
    public=ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe'
    early=ROOT/'build/pride-bounce-owner-work/player/final-skip-probe'
    late=ROOT/'build/pride-bounce-owner-work/player/final-skip-late-probe'
    for folder in (early,late):assert digest(folder/'player.exe')==bound(folder/'build-report.json')['binary_sha256']
    source=ROOT/'build/pride-game-over-music/hard.tape';raw=source.read_bytes()
    tape=out/'neutral-after-final.tape';tape.write_bytes(raw[:2369*2]+bytes(4000*2))
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
    state=out/'public-3336.state';clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands={};records={};checks={}
    def run(label,exe,end,kind=None,save=False,load=False):
        folder=out/label;folder.mkdir();env=dict(clean)
        if kind:
            env.update(TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_FINAL_SKIP='1' if kind=='early' else '0',
                TLK_FINAL_LATE_SKIP='1' if kind=='late' else '0')
        command=list(map(str,[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--config',config,'--resource-profile',profile,'--input',tape,'--frames',end,'--lle',
            '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,end+1))),
            '--dump-window',folder/'window.png']))
        if save:command+=['--save-at',str(end),str(state)]
        if load:command+=['--load',str(state)]
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        rows=re.findall(PATTERN,(folder/'run.log').read_text());records[label]=rows
        points=list(csv.DictReader((folder/'points.csv').open())) if kind else []
        print(label,'complete',flush=True)
        return folder,points
    normal,_=run('public-3336',public,3336,save=True)
    control,control_points=run('control-3336',late/'player.exe',3336,'control')
    checks['read_only_control_all_3336_guest_fields']=records['public-3336']==records['control-3336'] and len(records['public-3336'])==3336
    checks['read_only_control_whole_client']=pixels(normal/'window.png')==pixels(control/'window.png')
    later,late_points=run('late-3000',late/'player.exe',3000,'late')
    extended,_=run('public-3344',public,3344,load=True)
    earlier,early_points=run('early-3000',early/'player.exe',3000,'early')
    music_field=lambda rows:int(next(r for r in rows if r['pc']=='c08c06')['field'])
    checks['late_scene_age_matches']=3336-music_field(control_points)==3000-music_field(late_points)
    checks['early_scene_age_matches']=3344-music_field(control_points)==3000-music_field(early_points)
    for name in ('early','late'):
        checks[name+'/every_prefatal_guest_field']=records[name+'-3000'][:2368]==records['public-3336'][:2368]
    comparisons=dict(late=pixels(later/'window.png')==pixels(normal/'window.png'),
        early=pixels(earlier/'window.png')==pixels(extended/'window.png'))
    paths=[Path(__file__),public,source,early/'build-report.json',late/'build-report.json']
    report=dict(result='PHASE_ALIGNED_CLIENTS_CAPTURED' if all(checks.values()) else 'INVALID_ALIGNMENT',
        checks=checks,commands=commands,phase_aligned_whole_client_matches=comparisons,
        neutral_input_after_fatal_field=2369,interpreter_only_experiments=True,
        final_life_gameplay_resource_enabled=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],comparisons,'required checks',checks,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
