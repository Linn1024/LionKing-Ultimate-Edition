"""Recover an already observed rightward control branch and prove its cold replay."""
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
    base=ROOT/'build/pride-rng-player3';parent=base/'width-plan6'
    rp=parent/'report.json';r=bound(rp)
    initial=parent/'best.polled.tape';assert digest(initial)==r['selected_tape_sha256']
    search_folder=base/'width-plan7';search_path=search_folder/'search.json'
    search=json.loads(search_path.read_text());node=search['generations'][1][0]
    assert node['info']['x']==822 and node['info']['y']==485
    used=int(re.search(r'tape_words_used=(\d+)',(search_folder/'anchor/game.log').read_text()).group(1))
    words=lambda p:list(struct.unpack('<'+'H'*(p.stat().st_size//2),p.read_bytes()))
    values=words(initial)[:used];actions=node['actions'];paths=[Path(__file__),rp,initial,search_path,search_folder/'anchor/game.log']
    for depth,action in enumerate(actions,1):
        parent_index=0 if depth==1 else next(i for i,n in enumerate(search['generations'][depth-2]) if n['actions']==actions[:depth-1])
        branch=search_folder/f"d{depth}-p{parent_index}-{action['name']}.polled.tape"
        values+=words(branch)[:action['consumed_polls']];paths.append(branch)
    out=base/'width-right-branch';out.mkdir();tape=out/'route.polled.tape'
    tape.write_bytes(struct.pack('<'+'H'*len(values),*values))
    probe=base/'width-right-branch-cold'
    subprocess.run([sys.executable,str(ROOT/'tools/probe_pride_width_route.py'),'--tape',str(tape),'--out',str(probe),'--frames','1800'],cwd=ROOT,check=True,timeout=120)
    chosen=ROOT/node['folder'];expected=chosen/'wram-1800.bin'
    assert (probe/'wram-1800.bin').read_bytes()==expected.read_bytes(), 'Recovered branch does not replay from power-on'
    paths.extend([expected,probe/'report.json',probe/'wram-1800.bin'])
    report=dict(result='PASS',waypoint=dict(frame=1800,player=[822,485]),
        original_source='https://tasvideos.org/10612S',author='ShgofcTAS',
        actions=actions,selected_tape_sha256=digest(tape),cold_full_wram_equal=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        ordinary_controller_inputs_only=True,loaded_states_in_final_replay=False,
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Rightward prefix cold full WRAM exact at1800',flush=True)


if __name__=='__main__':main()
