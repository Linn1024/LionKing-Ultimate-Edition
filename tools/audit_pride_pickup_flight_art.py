"""Review original pickup flight art and reproduce the fixed-sprite port gap."""
import csv
import argparse
import hashlib
import json
from pathlib import Path
import struct

from audit_scenes import ROOT,read_rom
from summarize_pride_practice import bound
from verify_windows import hashes,pixels


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='build/pride-pickup-flight-art')
    args=parser.parse_args();out=(ROOT/args.out).resolve()
    assert out.is_relative_to(ROOT/'build');out.mkdir()
    md_path=ROOT/'build/md-pickup-flight/report.json';md=bound(md_path)
    native_path=ROOT/'build/native-pickup-flight2/report.json';native=bound(native_path)
    assert md['result']==native['result']=='OBSERVED'
    assert md['initialized_fixed_flight_calls']==70 and native['fixed_active_flight_samples']==24
    assert not md['unreviewed_flight_poses'] and not native['unreviewed_flight_poses']
    external=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    original=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    # Original C196BC changes the byte at render+9. Fixed bit0x40 in
    # that byte is bit0x4000 of the combined draw+8 word, not bit0x0040.
    assert original[0x196ca:0x196d2]==bytes.fromhex('e2209d0900c2206b')
    palette=struct.unpack_from('>16H',external,0x1d78aa)
    expected=[(c>>1&7)|(c>>5&7)<<3|(c>>9&7)<<6 for c in palette]
    rows=list(csv.DictReader((md_path.parent/'calls.csv').open()))
    rows=[r for r in rows if r['level']=='1' and r['callback']==r['action'] and int(r['flags'],16)&0x40]
    assert len(rows)==70
    for row in rows:
        colors=[int(row['colors'][i:i+4],16) for i in range(0,64,4)]
        assert row['palette']=='0' and colors[1:]==expected[1:]
    metadata_path=ROOT/'tools/pride_npc_pairs.json'
    pairs={int(r['snes'],16):r for r in json.loads(metadata_path.read_text())['pairs'] if r['role']=='pickup'}
    supported={0xc528bc:0x94df4,0xc528dd:0x94e1c}
    assert {int(p,16) for p in native['poses']}==set(supported)
    assert {int(p,16) for p in md['poses']}==set(supported.values())
    assert all(int(pairs[p]['md'],16)==q and pairs[p]['native_palette']==pairs[p]['md_palette']==0
               for p,q in supported.items())
    paths=[Path(__file__),md_path,native_path,metadata_path]
    windows=ROOT/'build/pride-pickup-flight-windows';captures=[]
    for field,pose in ((1616,0xc528bc),(1780,0xc528dd)):
        samples=[]
        for source in ('snes','md'):
            stem=windows/f'{field}-{source}'
            picture=stem.with_suffix('.png');scene_path=stem.with_suffix('.json');log=stem.with_suffix('.log')
            scene=json.loads(scene_path.read_text())
            pieces=[p for p in scene['pieces'] if p['pose']==pose and p['fixed'] and p['kept']]
            assert scene['level']==0 and scene['latched_gameplay']['descriptor']==0x387 and pieces
            assert all(p['palette']==0 for p in pieces)
            samples.append((pixels(picture),hashes(log)))
            paths.extend([picture,scene_path,log,stem.with_suffix('.ini')])
        assert samples[0]==samples[1], 'Expected current fixed-sprite exclusion was not reproduced'
        captures.append(dict(field=field,pose=hex(pose),native_and_md_pickup_clients_identical=True,
                             guest_hashes_equal=True,visible_fixed_pieces=pieces))
    wide=ROOT/'engine/runner/tlk_wide.c'
    assert 'owner && !cub && !owner->fixed && s_md_level==0' in wide.read_text()
    paths.extend([wide,ROOT/'build/pride-player/build-report.json',ROOT/'build/pride-player/player.exe'])
    build=bound(paths[-2]);assert digest(paths[-1])==build['binary_sha256']
    report=dict(result='ORIGINAL_FLIGHTS_VERIFIED_PORT_GAP_REPRODUCED',
        observed_native_fixed_samples=24,observed_original_md_executed_fixed_calls=70,
        original_md_palette0_live_checks=70,reviewed_pose_pairs={hex(p):hex(q) for p,q in supported.items()},
        current_windows=captures,missing_asset_decode_required_for_these_two_flights=False,
        current_fixed_piece_exclusion_confirmed=True,production_mappings_unchanged=True,
        md_animation_timing_or_motion_equivalence_proven=False,other_pickup_transitions_verified=False,
        next_action='Add scene/actor/pose/palette guarded fixed-pickup artwork support; preserve other fixed-sprite fallbacks.',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'two original flight types; four actual Windows clients',flush=True)


if __name__=='__main__':main()
