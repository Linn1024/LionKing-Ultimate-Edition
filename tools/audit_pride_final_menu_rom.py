"""Trace sampled original final-menu sprites to ROM frame records and pixels."""
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_sprite_catalog import md_frame


def main():
    base=ROOT/'build/pride-final-menu-art-original';source=base/'report.json';data=bound(source)
    audit=ROOT/'build/pride-final-menu-art-audit/report.json';bound(audit)
    out=ROOT/'build/pride-final-menu-rom-audit';out.mkdir()
    rom=(ROOT/'Lion King, The (World).md').read_bytes()
    # Frame metadata is validated structurally, then independently checked
    # against actual submitted VDP tile bytes, dimensions and placement.
    frames={}
    for address in range(0,len(rom)-24,2):
        pieces=md_frame(rom,address)
        if pieces:frames[address]=pieces
    rows={};checks={};used_frames=set();coverage={}
    for case,observations in data['observations'].items():
        results=[]
        for age in (118,120,124,125,140,141,160,180,200,220):
            folder=base/case/str(age);vram=(folder/'vram.bin').read_bytes()
            row=next(r for r in observations if r['age']==age);sprites=[]
            for entry in row['sprites']:
                y,size,attr,x=entry['words'];w=((size>>10&3)+1)*8;h=((size>>8&3)+1)*8
                start=(attr&2047)*32
                payload=bytes(vram[((start+i)&65535)^1] for i in range(w*h//2))
                sprites.append(dict(index=entry['index'],x=(x&511)-128,y=(y&511)-128,
                    width=w,height=h,attr=attr,payload=payload))
            placements=[];covered=set()
            for address,pieces in frames.items():
                candidates=None;matches=[]
                for dx,dy,w,h,pointer in pieces:
                    raw=rom[pointer:pointer+w*h//2]
                    current={(s['x']-dx,s['y']-dy) for s in sprites
                        if s['width']==w and s['height']==h and s['payload']==raw and not s['attr']&0x1800}
                    if not current:candidates=set();break
                    candidates=current if candidates is None else candidates&current
                    if not candidates:break
                for x,y in sorted(candidates or ()):
                    indices=[]
                    for dx,dy,w,h,pointer in pieces:
                        indices.extend(s['index'] for s in sprites if s['x']==x+dx and s['y']==y+dy and
                            s['width']==w and s['height']==h and s['payload']==rom[pointer:pointer+w*h//2])
                    covered.update(indices);used_frames.add(address)
                    placements.append(dict(frame=hex(address),anchor=[x,y],sprite_indices=indices))
            visible={s['index'] for s in sprites if s['x']<320 and s['x']+s['width']>0 and
                s['y']<224 and s['y']+s['height']>0}
            unmatched=sorted(visible-covered)
            checks[case+str(age)+'_all_visible_sprite_tiles_from_rom']=not unmatched
            results.append(dict(age=age,sprite_count=len(sprites),visible_count=len(visible),
                unmatched_sprite_indices=unmatched,placements=placements))
        rows[case]=results
    metadata={hex(p):[dict(x=x,y=y,width=w,height=h,source=hex(s)) for x,y,w,h,s in frames[p]] for p in sorted(used_frames)}
    paths=[Path(__file__),source,audit,ROOT/'tools/pride_sprite_catalog.py',ROOT/'Lion King, The (World).md']
    report=dict(result='PASS' if all(checks.values()) else 'PARTIAL',checks=checks,
        structurally_valid_frame_records=len(frames),rows=rows,matched_frame_metadata=metadata,
        alias_policy='All exact candidate records retained; equal pixels do not prove unique live actor ownership',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),'pictures,',len(used_frames),'frame records',flush=True)


if __name__=='__main__':main()
