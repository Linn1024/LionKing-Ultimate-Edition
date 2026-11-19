"""Verify original directional hurt-state correspondence without hiding phase gaps."""
import hashlib
import json
from audit_scenes import ROOT, read_rom
from compare_pride_movement import value
from compare_pride_roll_originals import state


def main():
    s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    native_path=ROOT/'build/pride-activation-reactivation-contacts/snes.json'
    md_path=ROOT/'build/pride-roll-contacts/md.json'
    native=json.loads(native_path.read_text())['cases'];md=json.loads(md_path.read_text())['cases']
    catalog=json.loads((ROOT/'build/pride-sprites/catalog.json').read_text())
    poses={int(r['snes'],16):{int(p,16) for p in r['md']} for g in ('exact_matches','pixel_art_variants') for r in catalog[g]}
    results=[]
    for ns,ms,velocity in ((0xc35d6c,0x196b4c,65536),(0xc35f3c,0x196d04,-65536)):
        off=ns&0x3fffff
        assert s[off+0x43:off+0x46]==bytes.fromhex('a92800')
        assert s[off+0x4e:off+0x51]==bytes.fromhex('a91200')
        assert m[ms+0x2a:ms+0x30]==bytes.fromhex('243c00000028')
        assert m[ms+0x32:ms+0x38]==bytes.fromhex('223c00000012')
        assert s[off+0xb2:off+0xb5]==bytes.fromhex('a9fdff')
        assert int.from_bytes(s[off+0xc3:off+0xc5],'little',signed=True)==velocity//65536
        assert m[ms+0x98:ms+0xa0]==bytes.fromhex('237cfffd0000003c')
        assert int.from_bytes(m[ms+0xa2:ms+0xa6],'big',signed=True)==velocity
        entries=[]
        for name in native:
            left=next(((i,r) for i,r in enumerate(native[name]) if state(r,'snes')==ns),None)
            right=next(((i,r) for i,r in enumerate(md[name]) if state(r,'md')==ms),None)
            if left is None and right is None:continue
            assert left and right
            for source,entry in (('snes',left),('md',right)):
                assert value(entry[1],source,'vx')==velocity and value(entry[1],source,'vy')==-196608
                assert entry[1]['words'][22]==18
            assert right[1]['pose'] in poses[left[1]['pose']]
            entries.append({'case':name,'native_index':left[0],'md_index':right[0],
                            'phase_difference_retained':left[0]-right[0]})
        assert entries
        results.append({'snes':ns,'md':ms,'entry_velocity_q16':velocity,'entries':entries})
    out=ROOT/'build/pride-hurt-pairs';out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps({'result':'PASS','scope':__doc__,'state_pairs':results,
        'source_sha256':{'native':hashlib.sha256(native_path.read_bytes()).hexdigest(),'md':hashlib.sha256(md_path.read_bytes()).hexdigest()},
        'all_hurt_paths_proven':False},indent=2)+'\n')
    print('Original directional hurt states: ROM constants, live entry velocities/timers/art; phase gaps retained PASS',flush=True)


if __name__=='__main__':main()
