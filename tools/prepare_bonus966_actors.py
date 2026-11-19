"""Review static bonus-body/bug images against original MD artwork; addresses/maps only tracked."""
import collections,csv,json,re,struct
from pathlib import Path
from audit_scenes import ROOT
from pride_sprite_catalog import snes_frame,md_frame,bitmap
from build_pride_compiled_hooks import digest
out=ROOT/'build/bonus966-actors';out.mkdir(exist_ok=True);s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes();native=bytearray(s);native.extend(bytes(0x400000-len(native)));data=(ROOT/'build/bonus961-native/10/bonus.native.state').read_bytes();at=data.find(bytes.fromhex('dd05c0'))-0xdf;assert at>=0 and data[at+0x1ff9e:at+0x1ffa0]==b'\x0a\0';native[0x3e0000:]=data[at:at+0x20000];header=ROOT/'engine/generated/resources/pride_sprite_map.h';text=(ROOT/'build/bonus965-baseline/engine/generated/resources/pride_sprite_map.h').read_text();a=text.index('\n{');b=text.index('\n};',a);rows={int(re.match(r'\{0x([0-9a-f]+),',line)[1],16):line for line in text[a+1:b].splitlines()};old=dict(rows);pairs={};coverage={}
def shape(b):
 x,y,w,h,p=b;c={0:0};z=[]
 for v in p:
  if v not in c:c[v]=len(c)
  z.append(c[v])
 return w,h,bytes(z)
def decode(raw,p,md):
 f=md_frame(raw,p) if md else snes_frame(raw,p,ram_banks=True)
 if not f:return None
 try:
  b=bitmap(raw,f,md,with_origin=True);return b if len(b)==5 and b[2] and b[3] else None
 except (ValueError,IndexError,struct.error):return None
def color(v):
 c=[((v>>sh)&7)*4+(((v>>sh)&7)>>2) for sh in (1,5,9)];return c[0]|c[1]<<5|c[2]<<10
def dist(a,b):return sum(w*(((a>>sh)&31)-((b>>sh)&31))**2 for sh,w in [(0,3),(5,6),(10,2)])
for name,slo,shi,mranges,role,bank,pal,owners in [
 ('pumbaa',0x52c00,0x53b00,[(0x18b000,0x18cc18)],21,3,0x50ada,[dict(level=10,descriptor='0xc5858a')]),
 ('timon_throw',0x55e00,0x562ef,[(0x18cc18,0x18d800)],22,3,0x50ada,[dict(level=10,descriptor='0xc58a71')]),
 ('timon_hunt',0x562ef,0x56e00,[(0x87000,0x8a000)],22,4,0x3d3e1,[dict(level=n,descriptor='0xc5858a') for n in (11,12,13)]),
 ('bugs',0x52900,0x52c00,[(0x94000,0x96000)],4,0,0x7c93,[dict(level=10,descriptor=d) for d in ('0xc58999','0xc589a5')]+[dict(level=n,descriptor=d) for n in (11,12,13) for d in ('0xc58a11','0xc58a1d','0xc58a29','0xc58a35','0xc58a41','0xc58975')])]:
 if name=='timon_hunt':
  state=(ROOT/'build/bonus962-native/13/bonus.native.state').read_bytes();off=state.find(bytes.fromhex('7306c0'))-0xdf;assert off>=0 and state[off+0x1ff9e:off+0x1ffa0]==b'\x0d\0';native[0x3e0000:]=state[off:off+0x20000]
 index=collections.defaultdict(list);mdimages={}
 for lo,hi in mranges:
  for q in range(lo,hi,2):
   z=decode(m,q,True)
   if z:mdimages[q]=z;index[shape(z)].append(q)
 ca=struct.unpack_from('<16H',s,pal);mb=0 if bank==0 else 3;cb=[color(v) for v in struct.unpack_from('>16H',m,0x27d19c+mb*32)];native_count=matched=0
 for p in range(slo,shi):
  z=decode(native,p,False)
  if not z:continue
  native_count+=1;qs=index.get(shape(z),[])
  if not qs:continue
  oldq=int(re.match(r'\{0x[0-9a-f]+, 0x([0-9a-f]+),',rows[p])[1],16) if p in rows else None
  if oldq is not None and oldq not in qs:continue
  q=oldq if oldq is not None else min(qs,key=lambda q:sum(abs(x-y) for x,y in zip(z[:2],mdimages[q][:2])));v=collections.defaultdict(collections.Counter)
  for x,y in zip(z[4],mdimages[q][4]):
   if x and y:v[x][y]+=1
  nm=[0]+[v[i].most_common(1)[0][0] if v[i] else min(range(1,16),key=lambda j:dist(ca[i],cb[j])) for i in range(1,16)];mn=[0]+[min(range(1,16),key=lambda j:dist(cb[i],ca[j])) for i in range(1,16)];pair=dict(snes=hex(p),md=hex(q),role=role,native_palette=bank,md_palette=mb,native_to_md=nm,md_to_native=mn,owners=owners,basis='native body-bank/static bug image and exact occupied pixel/index correspondence',family=name);pairs[p]=pair;matched+=1
  # Existing semantic pickup mappings are shared unchanged; other old entries
  # were default cub-only images and now receive an owned bonus role.
  if p in rows and rows[p].count(',')>14 and role==4:continue
  x,y,w,h,_=mdimages[q];rows[p]=f'{{0x{p:x}, 0x{q:x}, {x}, {y}, {w}, {h}, 0, {{{{0,0,0}}}},{role},{bank},{mb}, {{'+','.join(map(str,mn))+'}, {'+','.join(map(str,nm))+'}},'
 coverage[name]=dict(native_headers=native_count,matched=matched,md_headers=len(mdimages));print(name,coverage[name],flush=True)

# Original timed frame streams provide correspondence where the artwork itself
# differs. Timings remain native; no target code is consulted at runtime.
def stream(raw,at,md,lo,hi):
 result=[]
 while 0<raw[at]<128:
  p=int.from_bytes(raw[at+1:at+4],'big' if md else 'little')
  if not lo<=p<hi:break
  result.append((raw[at],p));at+=4
 return result
for ns,ms,role,bank,palette,family,owners in [
 (0x26131,0x17ec44,22,3,0x50ada,'timon_throw',[dict(level=10,descriptor='0xc58a71')]),
 (0x26161,0x17ec74,22,3,0x50ada,'timon_throw',[dict(level=10,descriptor='0xc58a71')]),
 (0x26199,0x17ec96,22,3,0x50ada,'timon_throw',[dict(level=10,descriptor='0xc58a71')]),
 (0x262a1,0x17ed1a,21,3,0x50ada,'pumbaa',[dict(level=10,descriptor='0xc5858a')]),
 (0x26329,0x17eda2,21,3,0x50ada,'pumbaa',[dict(level=10,descriptor='0xc5858a')]),
 (0x26345,0x17edbe,21,3,0x50ada,'pumbaa',[dict(level=10,descriptor='0xc5858a')]),
 (0x2637d,0x17edf6,21,3,0x50ada,'pumbaa',[dict(level=10,descriptor='0xc5858a')])]:
 native_seq=stream(s,ns,False,0xc52c00,0xc562ef);md_seq=stream(m,ms,True,0x18b000,0x18d800);assert native_seq and [d for d,p in native_seq]==[d for d,p in md_seq],(hex(ns),hex(ms),len(native_seq),len(md_seq));ca=struct.unpack_from('<16H',s,palette);cb=[color(v) for v in struct.unpack_from('>16H',m,0x27d19c+96)]
 for (duration,p),(_,q) in zip(native_seq,md_seq):
  p &= 0x3fffff;previous=pairs.get(p)
  if previous and previous['md']==hex(q):continue
  z=decode(m,q,True);assert z,hex(q);x,y,w,h,_=z;nm=[0]+[min(range(1,16),key=lambda j:dist(ca[i],cb[j])) for i in range(1,16)];mn=[0]+[min(range(1,16),key=lambda j:dist(cb[i],ca[j])) for i in range(1,16)]
  pairs[p]=dict(snes=hex(p),md=hex(q),role=role,native_palette=bank,md_palette=3,native_to_md=nm,md_to_native=mn,owners=owners,family=family,basis=f'corresponding original timed animation streams {ns:06x}/{ms:06x}, duration{duration}')
  rows[p]=f'{{0x{p:x}, 0x{q:x}, {x}, {y}, {w}, {h}, 0, {{{{0,0,0}}}},{role},{bank},3, {{'+','.join(map(str,mn))+'}, {'+','.join(map(str,nm))+'}},'

# The original Hunt spawn tables enumerate the same eight bug kinds. Their
# shared update handlers and exact-image anchors establish type correspondence
# even when the individual MD drawings have different outlines.
for kind in range(8):
 nrec=0x58a11+kind*12;mrec=0x17eb20+kind*14
 p=int.from_bytes(s[nrec+6:nrec+9],'little')&0x3fffff;q=int.from_bytes(m[mrec+6:mrec+10],'big');z=decode(m,q,True);assert z
 if p in pairs and pairs[p]['md']==hex(q):continue
 ca=struct.unpack_from('<16H',s,0x7c93);cb=[color(v) for v in struct.unpack_from('>16H',m,0x27d19c)];nm=[0]+[min(range(1,16),key=lambda j:dist(ca[i],cb[j])) for i in range(1,16)];mn=[0]+[min(range(1,16),key=lambda j:dist(cb[i],ca[j])) for i in range(1,16)];owners=[dict(level=n,descriptor=hex(0xc00000+nrec)) for n in (11,12,13)]+[dict(level=10,descriptor=d) for d in ('0xc58999','0xc589a5')]
 pairs[p]=dict(snes=hex(p),md=hex(q),role=4,native_palette=0,md_palette=0,native_to_md=nm,md_to_native=mn,owners=owners,family='bugs',basis=f'original Hunt eight-kind spawn tables {nrec:06x}/{mrec:06x}, kind{kind}')
 x,y,w,h,_=z;rows[p]=f'{{0x{p:x}, 0x{q:x}, {x}, {y}, {w}, {h}, 0, {{{{0,0,0}}}},4,0,0, {{'+','.join(map(str,mn))+'}, {'+','.join(map(str,nm))+'}},'
coverage['original_phase_streams']=7
coverage['final_families']=dict(collections.Counter(p['family'] for p in pairs.values()))
file=ROOT/'tools/bonus_actor_pairs.json';file.write_text(json.dumps(dict(scope=__doc__,pairs=[pairs[p] for p in sorted(pairs)],coverage=coverage),indent=2)+'\n');header.write_text(text[:a+1]+'\n'.join(rows[p] for p in sorted(rows))+text[b:]);paths=[Path(__file__),file,header,ROOT/'build/bonus962-native/report.json',ROOT/'build/bonus959-reference/report.json'];(out/'report.json').write_text(json.dumps(dict(result='PREPARED',links=len(pairs),images=len(rows),previous_images=len(old),coverage=coverage,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('PREPARED',len(pairs),len(rows),flush=True)
