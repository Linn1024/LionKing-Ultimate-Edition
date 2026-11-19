"""Compare first-level terrain data without conflating profiles with triggers."""
from pathlib import Path
import importlib.util
import json
import struct
from collections import Counter
from audit_scenes import ROOT,read_rom

def main():
    s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    spec=importlib.util.spec_from_file_location('tlk_lz',ROOT/'engine/tools/re/decompress.py')
    lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    snes_record=0x387;md_record=0x1cfdb4
    sp=lambda offset:int.from_bytes(s[snes_record+offset:snes_record+offset+3],'little')&0x3fffff
    mp=lambda offset:struct.unpack_from('>I',m,md_record+offset)[0]
    collision=lz.decompress(s,sp(0))[0];sm=lz.decompress(s,sp(9))[0];mm=lz.decompress(m,mp(16))[0]
    sh,mh=sp(3),mp(8);matched=0;different=[];height_equal=0;full_height_equal=0;map_flag_differences=[];height_variants={}
    assert len(sm)==len(mm)==16000
    marker_positions={'snes':{},'md':{}}
    contact_targets={}
    for i in range(8000):
        sw=struct.unpack_from('<H',sm,i*2)[0];mw=struct.unpack_from('>H',mm,i*2)[0]
        si=sw&0xfff8;mi=mw&0xfff8
        if (sw&7)!=(mw&7):map_flag_differences.append({'x':i%100,'y':i//100,'snes':sw&7,'md':mw&7})
        sr=collision[si//2:si//2+4];mr=m[mp(4)+mi//2:mp(4)+mi//2+4]
        contact_targets.setdefault(si//8,{}).setdefault(mr[2],[]).append([i%100,i//100])
        for source,record in [('snes',sr),('md',mr)]:
            if record[3]:marker_positions[source].setdefault(hex(record[3]),[]).append([i%100*16,i//100*16])
        so=struct.unpack_from('<H',sr)[0];mo=mr[0]*16
        a=bytes(x&31 for x in s[sh+so:sh+so+16]);b=bytes(x&31 for x in m[mh+mo:mh+mo+16])
        height_equal+=a==b
        full_height_equal+=s[sh+so:sh+so+16]==m[mh+mo:mh+mo+16]
        sa=s[sh+so:sh+so+16];ma=m[mh+mo:mh+mo+16]
        if sa!=ma:
            key=sa.hex()+' -> '+ma.hex()
            variant=height_variants.setdefault(key,{'cells':0,'examples':[]})
            variant['cells']+=1
            if len(variant['examples'])<8:variant['examples'].append([i%100,i//100])
        if a==b and sr[2:]==mr[2:]:matched+=1
        else:different.append({'x':i%100,'y':i//100,'snes_block':si//8,'md_block':mi//8,
                               'snes_profile':a.hex(),'md_profile':b.hex(),'snes_flags':sr[2:].hex(),'md_flags':mr[2:].hex()})
    limit=max(struct.unpack_from('<H',collision,i)[0] for i in range(0,len(collision),4))+16
    report={'scope':'original static floor-height profiles; metadata semantics and dynamic collision remain separate',
            'matching_height_cells':height_equal,'total_cells':8000,'matching_profile_and_metadata_cells':matched,
            'height_table_bytes':limit,'height_table_low_five_bits_equal':all((s[sh+i]&31)==(m[mh+i]&31) for i in range(limit)),
            'matching_full_height_cells':full_height_equal,'height_table_all_bits_equal':s[sh:sh+limit]==m[mh:mh+limit],
            'height_byte_variants':height_variants,
            'map_low_flag_differences':map_flag_differences,
            'metadata_difference_counts':{a+' -> '+b:n for (a,b),n in Counter((d['snes_flags'],d['md_flags']) for d in different).items()},
            'contact_attribute_difference_cells':sum(d['snes_flags'][:2]!=d['md_flags'][:2] for d in different),
            'contact_record_alias_conflicts':[
                {'snes_block':block,'snes_attribute':collision[block*4+2],
                 'md_attributes_to_cell_coordinates':{str(tag):positions for tag,positions in targets.items()}}
                for block,targets in contact_targets.items() if len(targets)>1],
            'marker_positions':marker_positions,
            'metadata_or_profile_differences':different}
    out=ROOT/'build/pride-collision-audit.json';out.write_text(json.dumps(report,indent=2)+'\n')
    print(f'height profiles {height_equal}/8000; profiles plus raw metadata {matched}/8000; {len(different)} cells need semantic audit')
    for marker in ('0x12','0x29'):print('marker',marker,[(source,positions.get(marker)) for source,positions in marker_positions.items()])

if __name__=='__main__':main()
