"""Establish Return's original band table, initialization and live static background coverage."""
import csv,json,struct,sys,importlib.util
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
sys.path.insert(0,str(ROOT/'.tools/pythonlibs'))
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
out=ROOT/'build/return888-background';out.mkdir(exist_ok=True);m=(ROOT/'Lion King, The (World).md').read_bytes();cpu=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000);ins=list(cpu.disasm(m[0x8e7e8:0x8ea00],0x8e7e8));coeff=list(struct.unpack_from('>3H',m,0x8ea00));counts=[];count=0
for i in ins:
 if i.mnemonic=='move.w' and i.op_str=='d6, (a3)+':count+=1
 elif i.mnemonic=='move.w' and i.op_str=='(a4)+, d6':
  if count:counts.append(count);count=0
if count:counts.append(count)
assert len(counts)==3 and sum(counts)==224,(coeff,counts)
spec=importlib.util.spec_from_file_location('lz',ROOT/'engine/tools/re/decompress.py');lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz);rec=0x1cfdb4+8*48;bp=struct.unpack_from('>I',m,rec+24)[0];tp=struct.unpack_from('>I',m,rec+28)[0];pp=struct.unpack_from('>I',m,rec+44)[0];bg,_=lz.decompress(m,bp);tiles,_=lz.decompress(m,tp);used={int.from_bytes(bg[i:i+2],'big')&2047 for i in range(0,len(bg),2)};cases=[]
for row in csv.DictReader((ROOT/'build/later873-reference/scroll.csv').open()):
 if row['level']!='8':continue
 field=int(row['field']);folder=ROOT/'build/later873-reference';v=(folder/f'{field}-VRAM.bin').read_bytes();ram=(folder/f'{field}-68K RAM.bin').read_bytes();raw=(-struct.unpack_from('>H',v,0xfc00)[0])&1023;cx=min((raw+n*1024 for n in range(10)),key=lambda x:abs(x-int(row['camera_x'])));offsets=[struct.unpack_from('>H',v,0xfc02+y*4)[0]&1023 for y in range(224)];expected=[(-((cx*c)>>16))&1023 for c,n in zip(coeff,counts) for _ in range(n)];pal=(folder/f'{field}-CRAM.bin').read_bytes();vs=(folder/f'{field}-VSRAM.bin').read_bytes();r=dict(field=field,displayed_camera_x=cx,background_vscroll=int.from_bytes(vs[2:4],'big'),line_pointer=hex(int.from_bytes(ram[0xc60c:0xc610],'big')),scroll_errors=sum(a!=b for a,b in zip(offsets,expected)),names_match=bg==v[0xc000:0xc000+len(bg)],used_tiles_match=all(tiles[t*32:t*32+32]==v[t*32:t*32+32] for t in used),palette_matches=pal==m[pp:pp+128]);cases.append(r)
checks=dict(actual_captures=bool(cases),all_normal_static=all(r['names_match'] and r['used_tiles_match'] and r['palette_matches'] for r in cases),all_scroll=all(not r['scroll_errors'] and r['background_vscroll']==0 for r in cases));paths=[Path(__file__),ROOT/'build/later873-reference/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'OBSERVED',checks=checks,coefficients=coeff,band_lines=counts,source=dict(background=hex(bp),tiles=hex(tp),palette=hex(pp),background_bytes=len(bg),tile_bytes=len(tiles)),cases=cases,scope='Initializer08EA06 selects per-line scroll and clears pointer; update08E7E8 installs C610 and three224-line bands. Completed VDP hscroll, names, used tiles and palette are checked, not next-frame RAM rows.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(coeff,counts,checks,cases,flush=True)
