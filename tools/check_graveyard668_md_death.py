"""Continue the saved original MD opening skull through health death, without replaying earlier levels."""
import ctypes as C,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png
from build_pride_compiled_hooks import digest
reference=ROOT/'build/graveyard657-md-skull/report.json';out=ROOT/'build/graveyard668-md-death';out.mkdir();game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
for port in (0,1):game.core.retro_set_controller_port_device(port,513)
state=ROOT/'build/graveyard657-md-skull/entry/game.state';buf=C.create_string_buffer(state.read_bytes());game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool;assert game.core.retro_unserialize(buf,len(buf)-1)
w=lambda a:game.work_ram[a&65535]|game.work_ram[(a+1)&65535]<<8
p=lambda a:(w(a)<<16|w(a+2))&0xffffff
rows=[];death=None;health_restored=None
try:
    for field in range(13381,14981):
        game.step(128 if field<=13420 else 0);game.samples.clear();player=p(0xcd46)&65535;camera=w(0xcd36);health=w(0xccf6)
        if health==0 and death is None:death=field
        if death and health>0 and health_restored is None:health_restored=field
        if death:
            draw=w(player+12);row=dict(field=field,age=field-death,health=health,world=[w(player+8),w(player+10)],camera=[w(camera+8),w(camera+10)],draw=[w(draw),w(draw+2)],pose=hex(p(draw+10)),state=hex(p(player+0x30)));rows.append(row)
            if row['age'] in (0,24,60,120,180,224,248,274,300):png(out/(str(row['age'])+'.png'),*game.image)
finally:game.close()
paths=[Path(__file__),reference,state];(out/'frames.json').write_text(json.dumps(rows,separators=(',',':')))
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_DEATH_OBSERVED' if death and health_restored else 'INCOMPLETE',death=death,health_restored=health_restored,scope=__doc__,source_sha256={x.relative_to(ROOT).as_posix():digest(x) for x in paths},artifacts_sha256={x.relative_to(out).as_posix():digest(x) for x in out.rglob('*') if x.is_file() and x.name!='report.json'}),indent=2)+'\n');print('MD death',death,'health restored',health_restored);print(rows[::60][:6])
