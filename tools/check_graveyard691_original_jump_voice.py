"""Observe original MD opening-skull jump sound commands from its nearby checkpoint."""
import ctypes as C,json,csv,sys,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from md_lab import MdLab
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard691-original-jump-voice';out.mkdir(exist_ok=True);game=MdLab()
game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
for port in (0,1):game.core.retro_set_controller_port_device(port,513)
state=ROOT/'build/graveyard657-md-skull/entry/game.state';buf=C.create_string_buffer(state.read_bytes());game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool;assert game.core.retro_unserialize(buf,len(buf)-1)
trace=C.CDLL(str(ROOT/'build/md_commands.dll'));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p];assert trace.md_commands_init(game.core._handle,str(out/'commands.csv').encode())
w=lambda a:game.work_ram[a&65535]|game.work_ram[(a+1)&65535]<<8
p=lambda a:(w(a)<<16|w(a+2))&0xffffff
rows=[]
try:
 for field in range(13381,13801):
  trace.md_commands_frame(field);game.step(128 if field<=13420 else 0)
  for a in range(0x804e,0xff00,128):
   if p(a+4)==0x97964:rows.append(dict(field=field,actor=hex(a),x=w(a+8),y=w(a+10),state=hex(p(a+0x30))))
 with wave.open(str(out/'original.wav'),'wb') as wav:
  wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(round(game.av.timing.sample_rate));wav.writeframes(game.samples)
finally:trace.md_commands_close();game.close()
commands=list(csv.DictReader((out/'commands.csv').open()));relevant=[x for x in commands if int(x['selector']) in (2,19)]
(out/'actors.json').write_text(json.dumps(rows,separators=(',',':')))
paths=[Path(__file__),state,ROOT/'build/md_commands.dll']
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_OBSERVED',commands=relevant,jump_start_fields=[13615,13618],scope='Original MD checkpoint plus ordinary right40/neutral input, sound commands and PCM. No forced enemy state. Records physical inward leaps, distinct from vocal reaction and taunt states.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(relevant,flush=True)
