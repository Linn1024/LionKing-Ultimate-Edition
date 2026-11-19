"""Bound observed Pride artwork coverage at the actual next-level boundary."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--width',type=int,choices=(256,320),default=320)
    args=parser.parse_args();base=ROOT/'build/pride-rng-player2'
    parent=base/('completion-reference-unpaused2' if args.width==320 else 'completion-reference-unpaused256')/str(args.width)
    probe=base/'completion-pose-probe';probe_report=bound(probe/'report.json');assert probe_report['result']=='PASS'
    tracked=[r.split() for r in (probe/'route.ram').read_text().splitlines()]
    boundary=next(int(r[0]) for r in tracked if int(r[0])>1000 and int(r[6],16)==1)
    assert boundary==4420
    # Display width must not alter this route's guest timeline. Compare all
    # observed full-WRAM hashes before borrowing the320 boundary for256.
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    if args.width==256:
        wide=base/'completion-reference-unpaused2/320/aot'
        assert [(n,h) for n,_,h in rows(wide)]==[(n,h) for n,_,h in rows(parent/'aot')]
    out=base/'pride-coverage'/str(args.width);out.mkdir(parents=True)
    checks={};commands={};sources=[Path(__file__),probe/'report.json',base/'build-report.json',parent/'resources.ini',probe/'route.ram']
    tape=base/'controller-unpaused2/route.polled.tape';sources.append(tape)
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 1\n')
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_SPRITE_REPORT=str(folder/'coverage.json'))
        cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
             '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',parent/'resources.ini',
             '--input-polled',tape,'--frames',boundary-1,'--no-pace','--no-audio','--no-record',
             '--config',config,'--hash-at',boundary-1]
        if mode=='lle':cmd+=['--lle']
        commands[mode]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(commands[mode],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
        coverage=json.loads((folder/'coverage.json').read_text())
        checks[mode+'/exit']=result.returncode==0
        checks[mode+'/all_observed_pride_poses_mapped']=not coverage['missing_poses'] and not coverage['missing_npc_poses']
        baseline=parent/mode;sources.append(baseline/'run.log')
        expected=[row for row in rows(baseline) if int(row[0])==boundary-1]
        checks[mode+'/original_completion_prefix_exact']=len(expected)==1 and rows(folder)==expected
    paths=[p for p in out.rglob('*') if p.is_file() and p.name!='report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        first_next_level_field=boundary,coverage_fields=boundary-1,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in paths},
        exhaustive_pose_inventory_proven=False,full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
