"""Review original gorilla drawings outside the observed walkthrough repertoire."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
from audit_scenes import ROOT
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna810-actions';out.mkdir(exist_ok=True)
s=bytearray((ROOT/'Lion King, The (USA).sfc').read_bytes());s.extend(bytes(0x400000-len(s)));m=(ROOT/'Lion King, The (World).md').read_bytes()
old={int(r['snes'],16):int(r['md'],16) for r in json.loads((ROOT/'tools/hakuna_gorilla_pairs.json').read_text())['pairs']};links=dict(old);groups=[]
def tokens(rom,start,end,md):
 rows=[]
 for p in range(start,end-3):
  if not 0<rom[p]<128:continue
  pose=int.from_bytes(rom[p+1:p+4],'big' if md else 'little');at=pose if md else pose&0x3fffff
  if not (0x10a55c<=pose<0x10ccdc if md else 0xc01cc2<=pose<0xc03d00):continue
  frame=(md_frame if md else snes_frame)(rom,at)
  if frame:rows.append(dict(address=hex(p),duration=rom[p],pose=hex(pose)))
 return rows
for a,b,c,d in [(0x27ae9,0x27b05,0xe931c,0xe933a),(0x27b29,0x27b45,0xe9348,0xe9364),(0x27b49,0x27b6a,0xe9368,0xe938a),(0x27bf5,0x27c27,0xe93cc,0xe93fe),(0x27d43,0x27d56,0xe94d4,0xe94e8)]:
 n=tokens(s,a,b,False);z=tokens(m,c,d,True);print(hex(a),[(r['pose'],r['duration']) for r in n]);print(hex(c),[(r['pose'],r['duration']) for r in z]);groups.append(dict(native_range=[hex(a),hex(b)],md_range=[hex(c),hex(d)],native=n,md=z))
 # Only aligned original programs become candidate links. Truncated or unequal
 # groups require a corrected bound/context, never nearest-pose guessing.
 if len(n)==len(z) and all(x['duration']==y['duration'] for x,y in zip(n[1:],z[1:])) and (n[0]['duration']==z[0]['duration'] or a==0x27d43):
  for x,y in zip(n,z):
   p=int(x['pose'],16);q=int(y['pose'],16);assert p not in links or links[p]==q,(hex(p),hex(q),hex(links[p]));links[p]=q
new=[dict(snes=hex(p),md=hex(q)) for p,q in sorted(links.items()) if p not in old]
canvas=Image.new('RGB',(1024,max(220,((len(new)+7)//8)*160)),(32,32,32));draw=ImageDraw.Draw(canvas)
palette=int.from_bytes(m[0x1cfdb4+5*48+44:0x1cfdb4+5*48+48],'big')+96
colors=[]
for i in range(16):
 v=int.from_bytes(m[palette+i*2:palette+i*2+2],'big');colors.append(tuple(((v>>sh)&7)*255//7 for sh in (1,5,9)))
for i,r in enumerate(new):
 q=int(r['md'],16);x,y,w,h,pix=bitmap(m,md_frame(m,q),True,with_origin=True);im=Image.new('RGB',(w,h));im.putdata([colors[c] if c else (32,32,32) for c in pix]);im=im.resize((w*2,h*2),Image.Resampling.NEAREST);ox=i%8*128;oy=i//8*160;canvas.paste(im,(ox,oy+25));draw.text((ox,oy),r['snes']+' /\n'+r['md'],fill='white')
canvas.save(out/'additional-md.png')
paths=[Path(__file__),ROOT/'tools/hakuna_gorilla_pairs.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',groups=groups,additional_pairs=new,total=len(links),landing_pause=dict(native=59,md=11,scope='normal landing program; alternate program retains59 in both originals; gameplay not changed by art mapping'),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('Additional',len(new),'total',len(links))
