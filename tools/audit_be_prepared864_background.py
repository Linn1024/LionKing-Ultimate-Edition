"""Inventory Be Prepared initialization, actual uniform scroll and live tile/palette changes."""
import json,csv,struct,sys,importlib.util
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
sys.path.insert(0,str(ROOT/'.tools/pythonlibs'))
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
out=ROOT/'build/be-prepared864-background';out.mkdir(exist_ok=True)
m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5');c=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
spec=importlib.util.spec_from_file_location('lz',ROOT/'engine/tools/re/decompress.py');lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
rec=0x1cfdb4+7*48;tileptr=struct.unpack_from('>I',m,rec+28)[0];bgptr=struct.unpack_from('>I',m,rec+24)[0];palptr=struct.unpack_from('>I',m,rec+44)[0];tiles,_=lz.decompress(m,tileptr);bg,_=lz.decompress(m,bgptr);used={int.from_bytes(bg[i:i+2],'big')&2047 for i in range(0,len(bg),2)}
listing='\n'.join(f'{i.address:06x} {i.mnemonic} {i.op_str}' for i in c.disasm(m[0x8e77c:0x8e7e8],0x8e77c));(out/'listing.txt').write_text(listing+'\n');cases=[]
for row in csv.DictReader((ROOT/'build/next824-reference/scroll.csv').open()):
 if row['level']!='7':continue
 field=int(row['field']);folder=ROOT/'build/next824-reference';v=(folder/f'{field}-VRAM.bin').read_bytes();ram=(folder/f'{field}-68K RAM.bin').read_bytes();pal=(folder/f'{field}-CRAM.bin').read_bytes();vs=(folder/f'{field}-VSRAM.bin').read_bytes()
 camera=int(row['camera_x']);raw=(-struct.unpack_from('>H',v,0xfc00)[0])&1023;cx=min((raw+n*1024 for n in range(10)),key=lambda x:abs(x-camera));scroll=struct.unpack_from('>H',v,0xfc02)[0]&1023
 changes=[t for t in sorted(used) if tiles[t*32:t*32+32]!=v[t*32:t*32+32]];palette_changes=[i for i in range(64) if m[palptr+i*2:palptr+i*2+2]!=pal[i*2:i*2+2]]
 cases.append(dict(field=field,camera_ram=camera,displayed_camera_x=cx,background_scroll=scroll,expected_half_x=(-int(cx/2))&1023,background_vscroll=int.from_bytes(vs[2:4],'big'),names_match=bg==v[0xc000:0xc000+len(bg)],background_used_tile_changes=changes,palette_changes=palette_changes,cleared_table_pointer=int.from_bytes(ram[0xc60c:0xc610],'big')))
checks=dict(actual_captures=bool(cases),all_uniform_half_x=all(r['background_scroll']==r['expected_half_x'] and r['background_vscroll']==0 for r in cases),line_table_disabled=all(r['cleared_table_pointer']==0 for r in cases))
paths=[Path(__file__),ROOT/'build/next824-reference/report.json',ROOT/'engine/runner/tlk_md_assets.c']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',checks=checks,scope='Original7 initializer clears the RAM line-table pointer and selects VDP register11 mode0 (full-plane scroll). C610 row data is leftover from Destiny, not active7 scroll evidence. Actual completed uniform scroll comes from FC00/FC02. Readiness7 remains disabled; this inventories static source coverage and live changes before renderer implementation.',source=dict(background=hex(bgptr),tiles=hex(tileptr),palette=hex(palptr),background_bytes=len(bg),tile_bytes=len(tiles),background_used_tiles=len(used)),cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks);print('coverage',len(bg),len(tiles));print(cases,flush=True)
