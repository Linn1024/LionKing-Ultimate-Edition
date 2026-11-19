"""Review actual owned Hakuna/Destiny artwork with initialized scene banks.

Research only: matches do not prove animation, behavior, voice or full coverage.
"""
import csv,hashlib,json,re,collections
from pathlib import Path
from PIL import Image,ImageDraw
from audit_scenes import ROOT
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna792-actors';out.mkdir(exist_ok=True)
s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes();native={};external={};sources=[]
for level,folder,field in ((5,ROOT/'build/hakuna790-route/34500',34000),(6,ROOT/'build/hakuna781-native',38000)):
 if level==5:state=folder/'current.state';scene=folder/'scene.json';log=folder/'run.log'
 else:state=ROOT/'build/hakuna784-windows/6/entry.native.state';scene=ROOT/'build/hakuna784-windows/6/scene.json';log=ROOT/'build/hakuna784-windows/6/run.log'
 # The level6 entry and its180-field idle continuation have different hashes.
 # Use the native saved38000 state and locate WRAM by its layout, then bind it
 # to the save payload and explicit scene/actor evidence rather than a later hash.
 data=state.read_bytes();desc=0xc00481 if level==5 else 0xc004b3;needle=desc.to_bytes(3,'little');positions=[];start=0
 expected=re.findall(r'wram_sha256=([a-f0-9]+)',log.read_text())[-1] if level==5 else None
 while (at:=data.find(needle,start))>=0:
  start=at+1;p=at-0xdf
  if p>=0 and p+0x20000<=len(data) and data[p+0x1ff9e:p+0x1ffa0]==level.to_bytes(2,'little'):
   if expected is None or hashlib.sha256(data[p:p+0x20000]).hexdigest()==expected:positions.append(p)
 assert len(positions)==1,(level,positions)
 work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3e0000:]=data[positions[0]:positions[0]+0x20000];native[level]=work
 work=bytearray(m);work.extend(bytes(0x1000000-len(work)));mdram=ROOT/f'build/hakuna780-reference/{field}-68K RAM.bin';work[0xff0000:]=mdram.read_bytes();external[level]=work;sources.extend((state,mdram))
ns=list(csv.DictReader((ROOT/'build/hakuna781-native/poses.csv').open()));ms=list(csv.DictReader((ROOT/'build/hakuna780-reference/poses.csv').open()))
def image(rom,pose,md):
 p=int(pose,16)&(0xffffff if md else 0x3fffff);f=(md_frame if md else snes_frame)(rom,p)
 if not f:return None
 b=bitmap(rom,f,md,with_origin=True);return b if len(b)==5 else None
def norm(b,mask=False):
 if b is None:return None
 # Storage tiles can pad otherwise identical art differently. Compare the
 # occupied rectangle; keep the original draw origin in later frame metadata.
 x0,y0,w,h,data=b;points=[(i%w,i//w) for i,c in enumerate(data) if c]
 if not points:return None
 left=min(x for x,y in points);right=max(x for x,y in points)+1
 top=min(y for x,y in points);bottom=max(y for x,y in points)+1
 data=bytes(data[y*w+x] for y in range(top,bottom) for x in range(left,right))
 colors={0:0};pixels=[]
 for c in data:
  if c not in colors:colors[c]=len(colors)
  pixels.append(bool(c) if mask else colors[c])
 return right-left,bottom-top,bytes(pixels)
reports=[]
for level in (5,6):
 mdrows=[r for r in ms if int(r['level'])==level and 0<int(r['descriptor'],16)<0x300000]
 mb={r['pose']:image(external[level],r['pose'],True) for r in mdrows};indexed=collections.defaultdict(list);masks=collections.defaultdict(list)
 for p,b in mb.items():
  if b:indexed[norm(b)].append(p);masks[norm(b,True)].append(p)
 groups=collections.defaultdict(dict)
 for r in ns:
  if not (0xc00000<int(r['descriptor'],16)<0xf00000):continue
  if (int(r['frame'])<36500)!=(level==5):continue
  groups[r['descriptor']][r['pose']]=r
 for desc,poses in groups.items():
  nb={p:image(native[level],p,False) for p in poses};pairs=[];missing=[];votes=collections.Counter()
  for p,b in nb.items():
   exact=indexed.get(norm(b),[]) if b else [];sil=masks.get(norm(b,True),[]) if b else []
   if exact or sil:
    candidates=exact or sil;owners=sorted({r['descriptor'] for r in mdrows if r['pose'] in candidates});votes.update(owners)
    pairs.append(dict(snes=p,md=candidates,basis='occupied image modulo color labels' if exact else 'occupied opacity silhouette',native_palette=poses[p]['palette'],md_owners=owners))
   else:missing.append(dict(pose=p,decoded=bool(b),size=b[2:4] if b else None))
  row=dict(level=level,native_descriptor=desc,native=len(poses),decoded=sum(b is not None for b in nb.values()),owner_votes=dict(votes),pairs=pairs,missing=missing);reports.append(row)
  if len(poses)<3:continue
  sheet=Image.new('RGB',(1024,420),(32,32,32));draw=ImageDraw.Draw(sheet)
  chosen=list(nb)[:8];mdchosen=list(dict.fromkeys(q for pair in pairs for q in pair['md']))[:8]
  if desc=='c58a7f':mdchosen=list(dict.fromkeys(r['pose'] for r in mdrows if r['descriptor']=='0e9250'))[:8]
  for y,rom,ps,md in ((0,native[level],chosen,False),(210,external[level],mdchosen,True)):
   for i,p in enumerate(ps):
    b=image(rom,p,md)
    if not b:continue
    x0,y0,w,h,pix=b;im=Image.new('RGB',(w,h));im.putdata([((c*17)%256,(c*47)%256,(c*97)%256) if c else (32,32,32) for c in pix]);im=im.resize((w*2,h*2),Image.Resampling.NEAREST);sheet.paste(im,(i*128,y+25));draw.text((i*128,y),('MD ' if md else 'SNES ')+p,fill='white')
  sheet.save(out/f'{level}-{desc}.png');print(level,desc,len(poses),'decoded',row['decoded'],'paired',len(pairs),'owners',dict(votes),flush=True)
sources += [Path(__file__),ROOT/'build/hakuna781-native/poses.csv',ROOT/'build/hakuna780-reference/poses.csv']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,families=reports,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources}),indent=2)+'\n')
