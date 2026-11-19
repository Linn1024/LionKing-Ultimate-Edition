"""Locate original gorilla animation groups for explicit cross-version artwork links."""
import csv,json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna798-streams';out.mkdir(exist_ok=True);groups={}
for name,file,romname,desc,endian in (('snes','build/hakuna781-native/poses.csv','Lion King, The (USA).sfc','c58a7f','little'),('md','build/hakuna780-reference/poses.csv','Lion King, The (World).md','0e9250','big')):
 rows=[r for r in csv.DictReader((ROOT/file).open()) if r['descriptor']==desc];poses={int(r['pose'],16) for r in rows};rom=(ROOT/romname).read_bytes();tokens={}
 for pose in poses:
  start=0;needle=pose.to_bytes(3,endian)
  while (p:=rom.find(needle,start))>=0:
   start=p+1
   if p and 0<rom[p-1]<128:tokens[p-1]=(rom[p-1],pose)
 starts=[p for p in tokens if p-4 not in tokens];result=[]
 for p in sorted(starts):
  seq=[];q=p
  while q in tokens:
   duration,pose=tokens[q];seq.append(dict(duration=duration,pose=hex(pose)));q+=4
  if len(seq)<2:continue
  result.append(dict(address=hex(p),frames=seq))
 groups[name]=result
 for r in result:print(name,r['address'],' '.join(f"{x['pose']}:{x['duration']}" for x in r['frames']),flush=True)
paths=[Path(__file__),ROOT/'build/hakuna793-gorilla/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',groups=groups,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
