"""Inspect retained fresh-reference differences and the first current raw sample."""
import collections
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
a=json.loads((ROOT/'build/pride-contact168-md/md.json').read_text())['cases']
b=json.loads((ROOT/'build/pride-roll-contacts/md.json').read_text())['cases']
for name,rows in a.items():
    differences=collections.Counter(k for x,y in zip(rows,b[name]) for k in x.keys()|y.keys() if x.get(k)!=y.get(k))
    physical=[dict(index=i,fresh={k:x[k] for k in ('x','y','health','pose')},prior={k:y[k] for k in ('x','y','health','pose')}) for i,(x,y) in enumerate(zip(rows,b[name])) if any(x[k]!=y[k] for k in ('x','y','health','pose'))]
    print(name,'different keys',dict(differences),'first physical',physical[:2],flush=True)
    fresh=rows[0]['raw_slots'];prior=b[name][0]['raw_slots']
    for x,y in zip(fresh,prior):
        if x!=y:
            word_differences=[(i*2,u,v) for i,(u,v) in enumerate(zip(x['words'],y['words'])) if u!=v]
            print('first raw-slot difference',hex(x['actor']),hex(y['actor']),'keys',list(x.keys()),list(y.keys()),'word differences',word_differences[:8],flush=True)
            break
path=ROOT/'build/pride-contact167-current/long-roll-chase/samples.bin'
with path.open('rb') as f:
    for i in range(30):
        header=f.read(16);magic,field,pad,size=struct.unpack('<4I',header);ram=f.read(size)
        if i in (0,15,16,17,27,28):
            word=lambda at:struct.unpack_from('<H',ram,at)[0]
            print('current',i,field,hex(pad),word(0xb21b),word(0xb21d),word(0x2004),flush=True)
