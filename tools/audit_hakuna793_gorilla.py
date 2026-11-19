"""Bind gorilla idle artwork by original animation phases, not capture order.

This starts explicit mappings for materially different art; it is not runtime
code or a demand for cycle/transition equality. Other gorilla actions remain.
"""
import csv,json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna793-gorilla';out.mkdir(exist_ok=True)
s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes()
native=[0xc01cc2,0xc01d1d,0xc01d78,0xc01dd3];md=[0x10a55c,0x10a624,0x10a6ec,0x10a7c4];pattern=[0,1,2,3,2,1]*2
for rom,start,poses,endian in ((s,0x27a77,native,'little'),(m,0xe92c0,md,'big')):
 for i,phase in enumerate(pattern):
  p=start+i*4;assert rom[p]==3 and int.from_bytes(rom[p+1:p+4],endian)==poses[phase],(hex(start),i)
ns=list(csv.DictReader((ROOT/'build/hakuna781-native/poses.csv').open()));ms=list(csv.DictReader((ROOT/'build/hakuna780-reference/poses.csv').open()))
rows=[]
for p,q in zip(native,md):
 n=next(r for r in ns if r['descriptor']=='c58a7f' and int(r['pose'],16)==p)
 z=next(r for r in ms if r['level']=='5' and r['descriptor']=='0e9250' and int(r['pose'],16)==q)
 rows.append(dict(snes=hex(p),md=hex(q),native_palette=int(n['palette']),md_palette=int(z['palette']),native_action=n['action'],md_action=z['action'],basis='same phase in original twelve-token idle loop'))
paths=[Path(__file__),ROOT/'build/hakuna792-actors/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,pairs=rows,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('Original gorilla idle phases',len(rows))
