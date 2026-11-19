"""Compare original Pride generic marker flags and the offscreen queue contract."""
import hashlib
import json
import struct
from audit_scenes import ROOT,read_rom


def main():
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    markers=json.loads((ROOT/'build/pride-collision-audit.json').read_text())['marker_positions']
    rows=[]
    for marker in sorted(set(markers['snes'])|set(markers['md']),key=lambda x:int(x,16)):
        i=int(marker,16);a=0xbe11+i*6;b=0x92adc+i*8
        sf=int.from_bytes(snes[a:a+3],'little');mf=struct.unpack_from('>I',md,b)[0]
        assert sf==0xc0cbfc and mf==0x18d414,(marker,'Review non-generic marker separately')
        sd=int.from_bytes(snes[a+3:a+6],'little');mp=struct.unpack_from('>I',md,b+4)[0]
        native=snes[(sd&0x3fffff)+5];external=md[mp+5]
        rows.append({'marker':i,'native_descriptor':sd,'md_descriptor':mp,'native_flags':native,'md_flags':external})
    different=[r for r in rows if r['native_flags']!=r['md_flags']]
    assert len(rows)==13 and len(different)==1
    assert different[0]=={'marker':14,'native_descriptor':0xc58ca4,'md_descriptor':0x9798e,'native_flags':2,'md_flags':0}
    assert snes[0xcc36:0xcc38]==bytes.fromhex('b78e')
    # Both original out-of-bounds paths test the same origin-coordinate bit.
    assert snes[0xbb3c:0xbb43]==bytes.fromhex('890200f002a25e')
    assert md[0x928e0:0x928ec]==bytes.fromhex('082a000100436704282a005c')
    report={'result':'PASS','scope':__doc__,'generic_marker_types':rows,'only_different_type':14,
            'native_flag2_selects_original_coordinates':True,'md_flag0_selects_current_coordinates':True,
            'native_byte_load_pc':0xc0cc36,'native_offscreen_origin_test':0xc0bb3c,'md_offscreen_origin_test':0x928e0,
            'original_md_live_lifecycle_report':str(ROOT/'build/pride-spawn-initial/md.json'),
            'full_enemy_behavior_equivalence_proven':False}
    out=ROOT/'build/pride-reactivation-original';out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('All13 original generic marker types reviewed; only lizard14 origin flag differs (2 versus0) PASS',flush=True)


if __name__=='__main__':main()
