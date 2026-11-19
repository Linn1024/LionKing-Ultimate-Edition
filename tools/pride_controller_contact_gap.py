"""Index the later MD controller-route contact gap without hiding actor differences.

Uses ordinary-input native and original MD snapshots. Geometry is explanatory;
this does not prove constructor pairing, enemy behavior or full-level fidelity.
"""
import hashlib
import argparse
import json
import re
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from pride_actor_bounds_audit import bounds,overlap


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-md',action='store_true',help='Replay original inputs using the32-bit research Python/core')
    args=parser.parse_args()
    folder=ROOT/'build/pride-ceiling-next-gap'
    if args.capture_md:
        import ctypes as C
        from md_lab import MdLab
        rows=json.loads((ROOT/'build/md-next-levels-replay/frames.json').read_text())
        game=MdLab()
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        game.core.retro_set_controller_port_device(0,513)
        game.core.retro_set_controller_port_device(1,513)
        try:
            for row in rows[:1795]:
                game.step(row['pad']);game.samples.clear()
                if row['frame']>=1793:
                    (folder/f"md{row['frame']}-wram.bin").write_bytes(bytes(game.work_ram))
        finally:game.close()
    paths={'native':folder/'hl_wram_1405.bin','md':folder/'md1794-wram.bin'}
    samples={name:path.read_bytes() for name,path in paths.items()}
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    mapping={int(a,16):int(b,16) for a,b in re.findall(r'\{0x([0-9a-f]+),0x([0-9a-f]+),[0-3]\}',
        (ROOT/'engine/generated/resources/pride_hitbox_map.h').read_text())}
    observations={}
    for source,actors in [('native',[0xb213,0xb613,0xb793]),('md',[0x93ce,0x98ce])]:
        ram=samples[source]
        word=lambda address:struct.unpack_from('<H',ram,address)[0]
        found=[]
        for actor in actors:
            draw=word(actor+12);flags=word(draw+8)
            if source=='native':
                pose=int.from_bytes(ram[draw+10:draw+13],'little')&0x3fffff
                external=mapping[pose]
                flags=((flags&0x40)<<5)|((flags&0x80)<<5)
            else:
                pose=(word(draw+10)<<16|word(draw+12))&0xffffff;external=pose
            box=bounds(rom,external,word(actor+8),word(actor+10),flags,True)
            found.append({'actor':actor,'xy':[word(actor+8),word(actor+10)],
                          'pose':pose,'selected_md_pose':external,'selected_body_bounds':box})
        for enemy in found[1:]:enemy['overlaps_player']=overlap(found[0]['selected_body_bounds'],enemy['selected_body_bounds'])
        observations[source]=found
    assert observations['native'][0]['xy']==observations['md'][0]['xy']==[465,973]
    assert observations['native'][0]['selected_body_bounds']==observations['md'][0]['selected_body_bounds']
    assert not any(actor['overlaps_player'] for actor in observations['native'][1:])
    assert observations['md'][1]['overlaps_player']
    ram=samples['md'];pointer=struct.unpack_from('<H',ram,0x93ce+36)[0]<<16|struct.unpack_from('<H',ram,0x93ce+38)[0]
    assert pointer==0xffff98ce
    report={'result':'PARTIAL','scope':__doc__,'native_frame':1405,'md_frame':1794,
            'player_bounds_agree':True,'original_md_contact_actor':pointer,'observations':observations,
            'snapshot_sha256':{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in paths.items()},
            'enemy_behavior_and_constructor_pairing_proven':False,
            'next_work':'Trace porcupine initialization, active-list membership, trigger and motion from original code; do not substitute player jump constants.'}
    (folder/'contact-gap.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MD porcupine overlaps; native nearby porcupines miss despite equal player bounds. Enemy behavior remains PARTIAL.',flush=True)


if __name__=='__main__':main()
