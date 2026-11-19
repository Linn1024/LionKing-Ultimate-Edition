"""Resolve original final-menu ROM records with their live decoded RAM sources."""
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_sprite_catalog import md_frame


def menu_frame(rom,address):
    direct=md_frame(rom,address)
    if direct:return direct
    count=struct.unpack_from('>H',rom,address)[0]+1
    if not 1<=count<=80 or address+24+count*16>len(rom):return None
    w,h=struct.unpack_from('>2H',rom,address+6)
    if w>320 or h>224:return None
    pieces=[];total=0;have_ram=False
    for i in range(count):
        pw,ph,dx,dy,flags,transfer,source=struct.unpack_from('>6HI',rom,address+24+i*16)
        if pw not in (8,16,24,32) or ph not in (8,16,24,32):return None
        if flags>>8!=((pw//8-1)<<2|(ph//8-1)):return None
        dx=dx-65536 if dx&32768 else dx;dy=dy-65536 if dy&32768 else dy
        if abs(dx)>512 or abs(dy)>512:return None
        ram=0xff0000<=source<0x1000000
        if ram:
            if (source&65535)+pw*ph//2>65536:return None
            have_ram=True
        elif source+pw*ph//2>len(rom):return None
        pieces.append((dx,dy,pw,ph,source));total+=pw*ph//2
    return pieces if have_ram and total==struct.unpack_from('>H',rom,address+10)[0] else None


def main():
    base=ROOT/'build/pride-final-menu-art-original';source=base/'report.json';data=bound(source)
    audit=ROOT/'build/pride-final-menu-art-audit/report.json';bound(audit)
    out=ROOT/'build/pride-final-menu-ram-audit';out.mkdir()
    rom=(ROOT/'Lion King, The (World).md').read_bytes()
    # Frame metadata is validated structurally, then independently checked
    # against actual submitted VDP tile bytes, dimensions and placement.
    frames={}
    for address in range(0,len(rom)-24,2):
        pieces=menu_frame(rom,address)
        if pieces:frames[address]=pieces
    rows={};checks={};used_frames=set();coverage={}
    for case,observations in data['observations'].items():
        results=[]
        for age in (118,120,124,125,140,141,160,180,200,220):
            folder=base/case/str(age);vram=(folder/'vram.bin').read_bytes()
            memory=(folder/'work_ram.bin').read_bytes();memory=bytes(memory[i^1] for i in range(len(memory)))
            def source_bytes(pointer,size):
                return memory[pointer&65535:(pointer&65535)+size] if pointer>=0xff0000 else rom[pointer:pointer+size]
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
                    raw=source_bytes(pointer,w*h//2)
                    current={(s['x']-dx,s['y']-dy) for s in sprites
                        if s['width']==w and s['height']==h and s['payload']==raw and not s['attr']&0x1800}
                    if not current:candidates=set();break
                    candidates=current if candidates is None else candidates&current
                    if not candidates:break
                for x,y in sorted(candidates or ()):
                    indices=[]
                    for dx,dy,w,h,pointer in pieces:
                        indices.extend(s['index'] for s in sprites if s['x']==x+dx and s['y']==y+dy and
                            s['width']==w and s['height']==h and s['payload']==source_bytes(pointer,w*h//2))
                    covered.update(indices);used_frames.add(address)
                    placements.append(dict(frame=hex(address),anchor=[x,y],sprite_indices=indices))
            visible={s['index'] for s in sprites if s['x']<320 and s['x']+s['width']>0 and
                s['y']<224 and s['y']+s['height']>0}
            unmatched=sorted(visible-covered)
            checks[case+str(age)+'_rom_records_resolve_all_live_source_bytes']=not unmatched
            results.append(dict(age=age,sprite_count=len(sprites),visible_count=len(visible),
                unmatched_sprite_indices=unmatched,placements=placements))
        rows[case]=results
    metadata={hex(p):[dict(x=x,y=y,width=w,height=h,source=hex(s)) for x,y,w,h,s in frames[p]] for p in sorted(used_frames)}
    paths=[Path(__file__),source,audit,ROOT/'tools/pride_sprite_catalog.py',ROOT/'Lion King, The (World).md']
    report=dict(result='PASS' if all(checks.values()) else 'PARTIAL',checks=checks,
        source_pixel_scope='RAM-referencing records use observed decoded bank bytes; ROM decoder recipe still unproven',structurally_valid_frame_records=len(frames),rows=rows,matched_frame_metadata=metadata,
        alias_policy='All exact candidate records retained; equal pixels do not prove unique live actor ownership',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),'pictures,',len(used_frames),'frame records',flush=True)


if __name__=='__main__':main()
