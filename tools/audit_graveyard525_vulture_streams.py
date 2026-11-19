"""Inventory original vulture animation streams and their actual ordered frame references."""
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
s0=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712');s=bytearray(s0);s.extend(bytes(0x400000-len(s)));s[0x3e0000:]=(ROOT/'build/graveyard519-wram/wram.bin').read_bytes()
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
native={p|0xc00000:bitmap(s,f,False,with_origin=True) for p in range(0x3f014,0x3fe90) if (f:=snes_frame(s,p)) and len(bitmap(s,f,False,with_origin=True))==5}
md={p:bitmap(m,f,True,with_origin=True) for p in range(0xe7396,0xe87ae,2) if (f:=md_frame(m,p)) and len(bitmap(m,f,True,with_origin=True))==5}
def streams(rom,poses,endian):
    starts=set()
    def record(at):return at>=0 and at+4<=len(rom) and rom[at]<0x30 and int.from_bytes(rom[at+1:at+4],endian) in poses
    for p in poses:
        needle=p.to_bytes(3,endian);start=0
        while (i:=rom.find(needle,start))>=0:
            start=i+1;at=i-1
            if not record(at):continue
            while record(at-4):at-=4
            starts.add(at)
    result=[]
    for at in sorted(starts):
        initial=at;rows=[]
        while record(at):rows.append([rom[at],hex(int.from_bytes(rom[at+1:at+4],endian))]);at+=4
        if rows:result.append(dict(offset=hex(initial),prefix=rom[max(0,initial-4):initial].hex(),records=rows,tail=rom[at:at+10].hex()))
    return result
ns=streams(s0,native,'little');ms=streams(m,md,'big');out=ROOT/'build/graveyard525-vulture-streams';out.mkdir(exist_ok=True)
paths=[Path(__file__),ROOT/'build/graveyard519-wram/report.json',ROOT/'build/graveyard519-wram/wram.bin']
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_STREAM_INVENTORY',native_frames=[hex(p) for p in native],md_frames=[hex(p) for p in md],native_streams=ns,md_streams=ms,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('FRAMES',len(native),len(md));print('NATIVE',ns);print('MD',ms)
