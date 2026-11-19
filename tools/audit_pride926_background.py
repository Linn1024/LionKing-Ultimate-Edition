"""Audit Pride Rock cave background initialization, line bands and palette-cycle assets."""
import json,struct,sys,importlib.util
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
sys.path.insert(0,str(ROOT/'.tools/pythonlibs'));from capstone import *
out=ROOT/'build/pride926-background';out.mkdir(exist_ok=True);m=(ROOT/'Lion King, The (World).md').read_bytes();cpu=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000);counts=[];n=0
for i in cpu.disasm(m[0x8e2b0:0x8e4ac],0x8e2b0):
 if i.mnemonic=='move.w' and i.op_str=='(a4)+, d6':
  if n:counts.append(n);n=0
 elif i.mnemonic=='move.w' and i.op_str=='d6, (a3)+':n+=1
counts.append(n);coeff=list(struct.unpack_from('>3H',m,0x8e532));spec=importlib.util.spec_from_file_location('lz',ROOT/'engine/tools/re/decompress.py');lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz);rec=0x1cfdb4+9*48;bp,tp=struct.unpack_from('>2I',m,rec+24);bg,_=lz.decompress(m,bp);tiles,_=lz.decompress(m,tp);used={int.from_bytes(bg[i:i+2],'big')&2047 for i in range(0,len(bg),2)};cases=[]
for folder,fields in [('later873-reference',[54000,54500]),('pride921-reference',[55000,57000])]:
 for f in fields:
  root=ROOT/'build'/folder;v=(root/f'{f}-VRAM.bin').read_bytes();ram=(root/f'{f}-68K RAM.bin').read_bytes();vs=(root/f'{f}-VSRAM.bin').read_bytes();pal=(root/f'{f}-CRAM.bin').read_bytes();cam=int.from_bytes(ram[0xcd36:0xcd38],'big');cx=int.from_bytes(ram[cam+8:cam+10],'big');raw=(-int.from_bytes(v[0xfc00:0xfc02],'big'))&1023;cx=min((raw+k*1024 for k in range(10)),key=lambda x:abs(x-cx));offsets=[struct.unpack_from('>H',v,0xfc02+y*4)[0]&1023 for y in range(224)];expected=[(-((cx*c)>>16))&1023 for c,n in zip(coeff,counts) for _ in range(n)];phases=[i for i in range(3) if pal==m[0x8e538+i*128:0x8e538+(i+1)*128]]
  cases.append(dict(folder=folder,field=f,displayed_camera_x=cx,scroll_errors=sum(a!=b for a,b in zip(offsets,expected)),background_vscroll=int.from_bytes(vs[2:4],'big'),names_match=bg==v[0xc000:0xc000+len(bg)],used_tiles_match=all(tiles[t*32:t*32+32]==v[t*32:t*32+32] for t in used),palette_phases=phases))
checks=dict(bands=counts==[96,88,40] and coeff==[32768,16384,32768],all_static=all(r['names_match'] and r['used_tiles_match'] for r in cases),scroll=all(r['scroll_errors']==0 and r['background_vscroll']==0 for r in cases),normal_cycle=all(r['palette_phases'] for r in cases));paths=[Path(__file__),ROOT/'build/later873-reference/report.json'];(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'OBSERVED',checks=checks,coefficients=coeff,band_lines=counts,cases=cases,source=dict(background=hex(bp),tiles=hex(tp),cycle='0x08e538/0x08e5b8/0x08e638',initialize='0x08e25e',update='0x08e2b0'),scope='Cave/background recipe only. Native summit07DB and ending scenes require independent ownership; no assumption of identical layer initialization.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,cases,flush=True)
