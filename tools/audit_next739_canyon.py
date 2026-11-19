"""Compare actual canyon tile artwork, independently of perspective/raster timing."""
import json,struct,collections
from audit_scenes import ROOT
out=ROOT/'build/next739-canyon';out.mkdir(exist_ok=True)
s=(ROOT/'build/next735-palettes/3-vram.bin').read_bytes();m=(ROOT/'build/next726-reference/21000-VRAM.bin').read_bytes();scene=json.loads((ROOT/'build/next725-baseline/3-md/scene.json').read_text())
def normal(data):
 colors={0:0};result=[]
 for c in data:
  if c not in colors:colors[c]=len(colors)
  result.append(colors[c])
 return bytes(result)
md=collections.defaultdict(list)
for at in range(0,65536,32):
 pixels=bytes((m[at+i//2]>>(0 if i&1 else 4))&15 for i in range(64));md[normal(pixels)].append((at,pixels))
def native(at):
 return bytes(sum(((s[(at+y*2+(plane&1)+(16 if plane>=2 else 0))&65535]>>(7-x))&1)<<plane for plane in range(4)) for y in range(8) for x in range(8))
used=set();matched=0;missing=[];votes={i:collections.Counter() for i in range(128)}
for line in scene['lines']:
 if line['blank']:continue
 for layer in (0,1):
  if not (line['main']|line['sub'])&(1<<layer):continue
  base=((line['bgchr']>>(layer*4))&15)<<13;mapbase=(line['bgsc'][layer]&0xfc)<<9
  for cell in range(32*32):
   word=struct.unpack_from('<H',s,(mapbase+cell*2)&65535)[0];tile=word&1023;pal=word>>10&7;key=(base,tile,pal)
   if key in used:continue
   used.add(key);pixels=native(base+tile*32);matches=md.get(normal(pixels),[])
   if matches:matched+=1
   else:missing.append(dict(base=base,tile=tile,palette=pal))
report=dict(result='OBSERVED',unique_used=len(used),matched=matched,missing=missing)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('CANYON',len(used),matched,'missing',len(missing))
