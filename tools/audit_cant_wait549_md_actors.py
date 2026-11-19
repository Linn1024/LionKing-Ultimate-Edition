"""Identify retained original second-level sound callers by physical actor/draw ownership."""
import csv,json,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
frames=ROOT/'build/md-next-levels-replay/frames.json';commands=ROOT/'build/md-next-levels-replay/commands.csv';levels={x['frame']:x['level'] for x in json.loads(frames.read_text())};records=[];paths=[Path(__file__),frames,commands]
for row in csv.DictReader(commands.open()):
    field=int(row['frame'])
    if levels.get(field)!=1 or row['selector']!='19' or row['value'] not in ('5','8','10'):continue
    selected=(field-1)//100*100+1;p=ROOT/f'build/md-next-levels-replay/{selected:05d}-wram.bin'
    if not p.exists():continue
    ram=p.read_bytes();paths.append(p);word=lambda at:struct.unpack_from('<H',ram,at&65535)[0];long=lambda at:(word(at)<<16|word(at+2))&0xffffff
    actor=int(row['actor'],16);draw=word(actor+12);owned=0x8000<=draw<=0xffe8 and word(draw+4)==actor+8
    records.append(dict(sound_frame=field,snapshot=selected,value=row['value'],caller=row['outer_caller'],actor=hex(actor),descriptor=hex(long(actor+4)),owned=owned,pose=hex(long(draw+10)) if owned else None,position=[word(actor+8),word(actor+10)]))
out=ROOT/'build/cant-wait549-md-actors';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='RETAINED_CALLER_OWNERS',scope='Sparse original snapshots precede each sound; identity/lifetime can differ at the exact event and must be checked before mapping. No sound/gameplay change follows automatically.',records=records,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in dict.fromkeys(paths)}),indent=2)+'\n');print(records,flush=True)
