"""Review actual initialized late-scene actor images and palette ROM sources."""
import collections,csv,hashlib,json,re
from pathlib import Path
from audit_scenes import ROOT
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/later875-actors';out.mkdir(exist_ok=True);s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes();sources=[];ns=list(csv.DictReader((ROOT/'build/later872-route/poses.csv').open()));ms=list(csv.DictReader((ROOT/'build/later873-reference/poses.csv').open()));families=[];palettes={}
def normalized(b,mask=False):
 if b is None:return None
 x,y,w,h,data=b;occupied=[(i%w,i//w) for i,c in enumerate(data) if c]
 if not occupied:return None
 left=min(x for x,y in occupied);right=max(x for x,y in occupied)+1;top=min(y for x,y in occupied);bottom=max(y for x,y in occupied)+1;colors={0:0};pixels=[]
 for y in range(top,bottom):
  for x in range(left,right):
   c=data[y*w+x]
   if c not in colors:colors[c]=len(colors)
   pixels.append(bool(c) if mask else colors[c])
 return right-left,bottom-top,bytes(pixels)
def decode(work,p,md):
 p=int(p,16)&(0xffffff if md else 0x3fffff);f=(md_frame if md else snes_frame)(work,p)
 if not f:return None
 try:
  b=bitmap(work,f,md,with_origin=True);return b if len(b)==5 else None
 except (IndexError,ValueError):return None
for level,native_path,ref in [(7,'build/destiny863-handoff/be-prepared.native.state',43000),(8,'build/later872-route/later.native.state',52000)]:
 p=ROOT/native_path;data=p.read_bytes();start=0;positions=[];needle=(0xc00387+level*0x32).to_bytes(3,'little')
 while (a:=data.find(needle,start))>=0:
  start=a+1;at=a-0xdf
  if at>=0 and at+0x20000<=len(data) and data[at+0x1ff9e:at+0x1ffa0]==level.to_bytes(2,'little'):positions.append(at)
 assert len(positions)==1,(level,positions)
 native=bytearray(s);native.extend(bytes(0x400000-len(native)));native[0x3e0000:]=data[positions[0]:positions[0]+0x20000]
 r=ROOT/f'build/later873-reference/{ref}-68K RAM.bin' if level==8 else ROOT/f'build/next824-reference/{ref}-68K RAM.bin';external=bytearray(m);external.extend(bytes(0x1000000-len(external)));external[0xff0000:]=r.read_bytes();sources.extend((p,r))
 mdrows=[r for r in ms if int(r['level'])==level and 0<int(r['descriptor'],16)<0x300000];images={r['pose']:decode(external,r['pose'],True) for r in mdrows};index=collections.defaultdict(list);mask=collections.defaultdict(list)
 for pose,b in images.items():
  if b:index[normalized(b)].append(pose);mask[normalized(b,True)].append(pose)
 groups=collections.defaultdict(dict);native_rows=[r for r in ns if int(r['level'])==level]
 for r in native_rows:
  if int(r['descriptor'],16)>=0xc50000:groups[r['descriptor']][r['pose']]=r
 banks=collections.defaultdict(collections.Counter)
 for r in native_rows:banks[int(r['palette'])][r['colors']]+=1
 palettes[str(level)]={}
 for bank,counts in banks.items():
  variants=[]
  for colors,count in counts.most_common(3):
   values=[int(colors[i:i+4],16) for i in range(0,64,4)];raw=b''.join(v.to_bytes(2,'little') for v in values);hits=[];at=0
   while (at:=s.find(raw,at))>=0:hits.append(hex(at));at+=1
   variants.append(dict(count=count,rom_sources=hits,colors=values))
  palettes[str(level)][str(bank)]=variants
 for desc,poses in groups.items():
  pairs=[];missing=[];votes=collections.Counter()
  for pose,row in poses.items():
   b=decode(native,pose,False);exact=index.get(normalized(b),[]) if b else [];sil=mask.get(normalized(b,True),[]) if b else [];candidates=exact or sil
   if candidates:
    owners=sorted({r['descriptor'] for r in mdrows if r['pose'] in candidates});votes.update(owners);pairs.append(dict(snes=pose,md=candidates,basis='indexed labels' if exact else 'opacity only',native_palette=int(row['palette']),owners=owners))
   else:missing.append(dict(pose=pose,decoded=b is not None,dynamic_ram=(int(pose,16)&0x3fffff)>=0x3e0000))
  record=dict(level=level,native_descriptor=desc,poses=len(poses),paired=len(pairs),owner_votes=dict(votes),pairs=pairs,missing=missing);families.append(record);print(level,desc,len(poses),len(pairs),dict(votes),flush=True)
sources += [Path(__file__),ROOT/'build/later872-route/poses.csv',ROOT/'build/later873-reference/poses.csv']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,families=families,palettes=palettes,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources}),indent=2)+'\n')
