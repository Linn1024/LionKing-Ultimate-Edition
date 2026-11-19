"""Locate actual initialized palette sources and compare canyon tile artwork."""
import struct,json,collections
from audit_scenes import ROOT
s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes();out=ROOT/'build/next735-palettes';out.mkdir(exist_ok=True);rows=[]
for level in (3,4):
 raw=(ROOT/f'build/next725-baseline/{level}-md/entry.state').read_bytes();a=raw.index(b'PPU0');n=struct.unpack_from('<I',raw,a+4)[0];regs=n-(65536+512+512+32);start=a+8+regs;cgram=struct.unpack_from('<256H',raw,start)
 scene=json.loads((ROOT/f'build/next725-baseline/{level}-md/scene.json').read_text());assert list(cgram[128:144])==scene['obj_palette0']
 vram=raw[start+512+512+32:start+512+512+32+65536];(out/f'{level}-vram.bin').write_bytes(vram)
 row=dict(level=level,native_palette_offsets=[s.find(raw[start+i*32:start+(i+1)*32]) for i in range(16)],cgram=list(cgram));rows.append(row);print(level,row['native_palette_offsets'])
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',rows=rows),indent=2)+'\n')
