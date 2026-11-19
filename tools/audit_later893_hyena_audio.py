"""Inventory adult-hyena original sound call sites, separately from cub hyenas."""
import csv,collections,json,sys
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
sys.path.insert(0,str(ROOT/'.tools/pythonlibs'))
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
out=ROOT/'build/later893-hyena-audio';out.mkdir(exist_ok=True);m=(ROOT/'Lion King, The (World).md').read_bytes();cpu=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000);ins=list(cpu.disasm(m[0x1adeaa:0x1af800],0x1adeaa));calls=[]
for i,x in enumerate(ins):
 if x.mnemonic=='jsr' and x.op_str in ('$2210.l','$228a.l','$22a6.l','$2d0000.l'):
  context=ins[max(0,i-3):i+1];calls.append(dict(pc=hex(x.address),wrapper=x.op_str,context=[f'{p.address:06x} {p.mnemonic} {p.op_str}' for p in context]))
(out/'listing.txt').write_text('\n'.join(f'{x.address:06x} {x.mnemonic} {x.op_str}' for x in ins)+'\n');native=collections.Counter()
for folder in ('later872-route','later874-route'):
 for r in csv.DictReader((ROOT/f'build/{folder}/audio.csv').open()):
  b=bytes.fromhex(r['stack']);tag=int.from_bytes(b[2:4],'little');at=5 if tag==0x2d16 else 6 if tag==0x2d4d else -1
  if at<0:continue
  caller=int.from_bytes(b[at:at+3],'little')+1
  if 0xc1ae00<=caller<0xc1d000 and r['actor']!='b213':native[(r['level'],r['event'],hex(caller))]+=1
refs={str(level):[] for level in (7,8)}
for level in (7,8):
 for file in (ROOT/'build/next824-reference/VRAM-unused',):pass
 field=45000 if level==7 else 52000;v=(ROOT/f'build/later873-reference/{field}-VRAM.bin').read_bytes();refs[str(level)]=dict(adult_hud_at_d440=v[0xd440:0xd560]==m[0x8f318:0x8f438])
paths=[Path(__file__),ROOT/'build/later873-reference/report.json',ROOT/'build/later872-route/report.json',ROOT/'build/later874-route/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope='Adult-hyena action code1ADEAA..1AF800, with corresponding native C1 voice-call observations. Runtime voice adapter is not implemented by this audit. Driver/register coincidence alone is not ownership proof. Original7/8 adult HUD uploads independently verified.',original_calls=calls,native_calls=[dict(level=k[0],event=k[1],caller=k[2],count=v) for k,v in native.items()],hud=refs,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(calls,flush=True);print('native',list(native.items()),'HUD',refs,flush=True)
