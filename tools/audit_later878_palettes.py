"""Bind actual7/8/9 native actor palette banks to original ROM sources and MD CRAM."""
import collections,csv,json,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/later878-palettes';out.mkdir(exist_ok=True);s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes();rows=[]
for name in ('later872-route','later874-route'):rows+=list(csv.DictReader((ROOT/f'build/{name}/poses.csv').open()))
palettes={};checks={}
for level in (7,8,9):
 banks=collections.defaultdict(collections.Counter)
 for r in rows:
  if int(r['level'])==level and 0xc50000<=int(r['descriptor'],16)<0xc60000:banks[int(r['palette'])][r['colors']]+=1
 palettes[str(level)]={}
 for bank,counts in sorted(banks.items()):
  candidates=[]
  for raw,count in counts.most_common():
   colors=[int(raw[i:i+4],16) for i in range(0,64,4)];binary=b''.join(v.to_bytes(2,'little') for v in colors);at=s.find(binary)
   if at<0:
    tail=s.find(binary[2:]);at=tail-2 if tail>=2 else -1
   if at>=0:candidates.append(dict(count=count,source=hex(at),colors=colors))
  palettes[str(level)][str(bank)]=dict(observed_variants=len(counts),normal=candidates[0] if candidates else None,other_rom_variants=candidates[1:3])
 checks[f'{level}/observed_banks_resolved']=all(b['normal'] is not None for b in palettes[str(level)].values())
 refs=[p for p in (ROOT/'build/later873-reference').glob('*-CRAM.bin') if int(p.name.split('-')[0]) in ({45000,48000} if level==7 else {50000,51000,52000,53000} if level==8 else {54000,54500})]
 ptr=struct.unpack_from('>I',m,0x1cfdb4+level*48+44)[0];checks[f'{level}/actual_normal_md_cram']=any(p.read_bytes()==m[ptr:ptr+128] for p in refs)
 print(level,{bank:(r['normal']['source'] if r['normal'] else None,r['observed_variants']) for bank,r in palettes[str(level)].items()},checks[f'{level}/actual_normal_md_cram'],flush=True)
paths=[Path(__file__),ROOT/'build/later872-route/report.json',ROOT/'build/later874-route/report.json',ROOT/'build/later873-reference/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'OBSERVED',checks=checks,palettes=palettes,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
