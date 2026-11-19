"""Recover any retained controller-search node and verify its full cold WRAM."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--source-tape',type=Path,required=True);parser.add_argument('--depth',type=int,required=True)
    parser.add_argument('--index',type=int,default=0);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();plan=args.plan.resolve();parent=args.source_tape.resolve();out=args.out.resolve();out.mkdir()
    rp=plan/'report.json';report=bound(rp)
    # A later branch can fail while earlier captured nodes remain usable.
    # The final cold replay below verifies the selected node independently;
    # recovering it does not relabel the parent search as successful.
    assert report['result'] in ('PARTIAL','RUNNING')
    inherited=None
    if 'source_tape_sha256' in report:
        assert digest(parent)==report['source_tape_sha256']
    else:
        inherited=parent.parent/'report.json';prior=bound(inherited)
        assert digest(parent)==prior['selected_tape_sha256']
    sp=plan/'search.json';search=json.loads(sp.read_text());node=search['generations'][args.depth-1][args.index]
    assert node['info']['level']==0 and node['info']['health']>0
    frame=node['frame'];anchor=plan/'anchor/game.log'
    used=int(re.search(r'tape_words_used=(\d+)',anchor.read_text()).group(1))
    words=lambda p:list(struct.unpack('<'+'H'*(p.stat().st_size//2),p.read_bytes()))
    values=words(parent)[:used];actions=node['actions'];paths=[Path(__file__),rp,parent,sp,anchor]
    if inherited:paths.append(inherited)
    for depth,action in enumerate(actions,1):
        parent_index=0 if depth==1 else next(i for i,n in enumerate(search['generations'][depth-2]) if n['actions']==actions[:depth-1])
        branch=plan/f"d{depth}-p{parent_index}-{action['name']}.polled.tape"
        values+=words(branch)[:action['consumed_polls']];paths.append(branch)
    tape=out/'route.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(values),*values))
    probe=out/'cold'
    subprocess.run([sys.executable,str(ROOT/'tools/probe_pride_width_route.py'),'--tape',str(tape),
                    '--out',str(probe),'--frames',str(frame)],cwd=ROOT,check=True,timeout=120)
    expected=(ROOT/node['folder'])/f'wram-{frame}.bin';observed=probe/f'wram-{frame}.bin'
    assert expected.read_bytes()==observed.read_bytes(),'Recovered node differs from ordinary power-on replay'
    paths.extend([expected,observed,probe/'report.json'])
    result=dict(result='PASS',parent_report_status=report['result'],waypoint=dict(frame=frame,player=[node['info']['x'],node['info']['y']]),
        original_source='https://tasvideos.org/10612S',author='ShgofcTAS',actions=actions,
        selected_tape_sha256=digest(tape),cold_full_wram_equal=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        ordinary_controller_inputs_only=True,loaded_states_in_final_replay=False,
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(result['waypoint'],'cold full WRAM exact',flush=True)


if __name__=='__main__':main()
