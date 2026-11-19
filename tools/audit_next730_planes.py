"""Bind original Exile plane initialization and bands; inspect Stampede's separate scene."""
import json,csv,struct
from audit_scenes import ROOT
from md_assets import lz
m=(ROOT/'Lion King, The (World).md').read_bytes();out=ROOT/'build/next730-planes';out.mkdir(exist_ok=True)
rows=[]
for row in csv.DictReader((ROOT/'build/next726-reference/scroll.csv').open()):
 level=int(row['level']);frame=int(row['field']);rec=0x1cfdb4+level*48
 ptr=lambda at:int.from_bytes(m[rec+at:rec+at+4],'big')
 names=lz.decompress(m,ptr(24))[0];tiles=lz.decompress(m,ptr(28))[0]
 v=(ROOT/f'build/next726-reference/{frame}-VRAM.bin').read_bytes();ram=(ROOT/f'build/next726-reference/{frame}-68K RAM.bin').read_bytes()
 bands=[];offsets=[int(row['offsets'][i:i+4],16) for i in range(0,len(row['offsets']),4)]
 for i,x in enumerate(offsets):
  if not bands or bands[-1][2]!=x:bands.append([i,i+1,x])
  else:bands[-1][1]=i+1
 tile_errors=sum(a!=b for a,b in zip(v,tiles));swap=bytearray(v);swap[::2]=v[1::2];swap[1::2]=v[::2]
 r=dict(level=level,field=frame,names_bytes=len(names),tiles_bytes=len(tiles),name_bank=v.find(names),name_swapped_bank=bytes(swap).find(names),tile_errors=tile_errors,swapped_tile_errors=sum(a!=b for a,b in zip(swap,tiles)),bands=bands,camera=[int(row['camera_x']),int(row['camera_y'])],vsram=int(row['vsram']))
 if level==4:
  table=struct.unpack_from('>4H',m,0x8c17a);r['coefficients']=table
  cx=r['camera'][0];expected=[0]*152
  for n,c in zip((8,16,24,24),table):expected += [(-(cx*c>>16))&1023]*n
  r['scroll_errors']=sum(a!=b for a,b in zip(expected,offsets))
 rows.append(r);print(r)
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',rows=rows),indent=2)+'\n')
