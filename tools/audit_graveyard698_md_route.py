"""Original MD whole-Graveyard actor inventory from its existing level checkpoint."""
import ctypes as C,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from md_lab import MdLab,png
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard698-md-route';out.mkdir(exist_ok=True);game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
for port in (0,1):game.core.retro_set_controller_port_device(port,513)
state=ROOT/'build/graveyard657-md-skull/entry/game.state';buf=C.create_string_buffer(state.read_bytes());game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool;assert game.core.retro_unserialize(buf,len(buf)-1)
w=lambda a:game.work_ram[a&65535]|game.work_ram[(a+1)&65535]<<8
p=lambda a:(w(a)<<16|w(a+2))&0xffffff
source=ROOT/'build/md-next-levels-replay/frames.json';inputs=json.loads(source.read_text());seen={};rows=[];captures=[]
try:
 for field in range(13381,18721):
  game.step(inputs[field-1]['pad']);game.samples.clear();level=w(0xccce)
  if level!=3:continue
  for actor in range(0x804e,0xff00,128):
   draw=w(actor+12)
   if not 0x8000<=draw<=0xffe8 or w(draw+4)!=actor+8:continue
   pose=p(draw+10);desc=p(actor+4);palette=w(draw+8)>>13&3;key=(desc,pose,palette)
   if key not in seen:seen[key]=dict(field=field,actor=hex(actor),descriptor=hex(desc),pose=hex(pose),palette=palette,action=hex(p(actor+0x30)),xy=[w(actor+8),w(actor+10)])
  player=p(0xcd46)&65535;rows.append(dict(field=field,player=[w(player+8),w(player+10)],health=w(0xccf6)))
  if field in (13470,14000,15000,16000,17000,18000,18500):png(out/f'{field}.png',*game.image);captures.append(field)
finally:game.close()
paths=[Path(__file__),state,source]
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_INVENTORY',scope=__doc__,actors=list(seen.values()),captures=captures,last=rows[-1],source_sha256={x.relative_to(ROOT).as_posix():digest(x) for x in paths}),indent=2)+'\n');print('MD unique',len(seen),'descriptors',sorted({x['descriptor'] for x in seen.values()}),flush=True)
