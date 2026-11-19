"""Reach the original MD opening skull once, save it, then stand near its middle using ordinary inputs."""
import ctypes as C,json,struct,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard657-md-skull';out.mkdir();source=ROOT/'build/md-next-levels-replay/frames.json';inputs=json.loads(source.read_text());game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
for port in (0,1):game.core.retro_set_controller_port_device(port,513)
w=lambda a:game.work_ram[a&65535]|game.work_ram[(a+1)&65535]<<8
p=lambda a:(w(a)<<16|w(a+2))&0xffffff
rows=[];snapshots=[];start=time.monotonic()
try:
    for field in range(1,14181):
        pad=inputs[field-1]['pad'] if field<=13380 else 128 if field<=13420 else 0
        game.step(pad);game.samples.clear()
        if field==13301:assert bytes(game.work_ram)==(ROOT/'build/md-next-levels-replay/13301-wram.bin').read_bytes(),'Original prefix diverged'
        if field==13380:game.dump(out/'entry')
        if field>=13380:
            actors=[]
            for a in range(0x804e,0xff00,128):
                if p(a+4)==0x97964:actors.append(dict(actor=hex(a),xy=[w(a+8),w(a+10)],action=hex(p(a+0x30)),pose=hex(p(w(a+12)+10)),phase=w(a+0x2e),velocity=[w(a+0x3a),w(a+0x3e)]))
            player=p(0xcd46)&65535;rows.append(dict(field=field,player=[w(player+8),w(player+10)],health=w(0xccf6),actors=actors))
        if field in (13420,13520,13720,14020):png(out/f'{field}.png',*game.image);snapshots.append(field)
        if field%4000==0:print('MD reference',field,flush=True)
finally:game.close()
(out/'frames.json').write_text(json.dumps(rows,separators=(',',':')))
paths=[Path(__file__),source,ROOT/'build/md-next-levels-replay/13301-wram.bin']
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_SKULL_OBSERVED',seconds=time.monotonic()-start,scope=__doc__,snapshot_fields=snapshots,source_sha256={x.relative_to(ROOT).as_posix():digest(x) for x in paths},artifacts_sha256={x.relative_to(out).as_posix():digest(x) for x in out.rglob('*') if x.is_file() and x.name!='report.json'}),indent=2)+'\n');print(rows[-1],flush=True)
