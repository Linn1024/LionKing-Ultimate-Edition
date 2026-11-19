"""Observe ordinary MD Continue inputs during and after the final-life fade."""
import ctypes as C
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png


def protocol(name,age):
    if name=='early-tap':return 64|256 if age==89 else 0
    if name=='early-release':return 64|256 if 70<=age<=110 else 0
    if name=='held-through':return 64|256 if 70<=age<=150 else 0
    if name=='after-fade':return 64 if 122<=age<=127 else (256 if 130<=age<=133 else 0)
    return 0


def main():
    out=ROOT/'build/pride-final-input-reference';out.mkdir()
    source=ROOT/'build/md-next-levels-replay/frames.json';inputs=json.loads(source.read_text())
    fatal=14788;game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_serialize_size.restype=C.c_size_t
    game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    trace=C.CDLL(str(ROOT/'build/md_commands.dll'));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    observations={}
    try:
        for field in range(1,fatal):
            game.step(inputs[field-1]['pad'] if field<=4000 else (128 if field>5400 else 0));game.samples.clear()
        size=game.core.retro_serialize_size();state=C.create_string_buffer(size)
        assert game.core.retro_serialize(state,size);(out/'prefatal.state').write_bytes(state.raw)
        for name in ('neutral','early-tap','early-release','held-through','after-fade'):
            folder=out/name;folder.mkdir();assert game.core.retro_unserialize(state,size)
            assert trace.md_commands_init(game.core._handle,str(folder/'commands.csv').encode())
            captures=[];first_health=None
            for age in range(301):
                trace.md_commands_frame(fatal+age);game.step(128 if age==0 else protocol(name,age));game.samples.clear()
                word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                if age>0 and word(0xccf6)>0 and first_health is None:first_health=age
                if age in (89,100,120,121,130,144,180,300):
                    png(folder/f'{age}.png',*game.image)
                    captures.append(dict(age=age,health=word(0xccf6),lives=word(0xccee),level=word(0xccce)))
            trace.md_commands_close()
            commands=list(csv.DictReader((folder/'commands.csv').open()))
            music=[dict(age=int(r['frame'])-fatal,program=int(r['value'])) for r in commands if r['selector']=='1']
            observations[name]=dict(first_health=first_health,music=music,captures=captures)
            print(name,'health restored at',first_health,'music',music,flush=True)
    finally:game.close()
    paths=[Path(__file__),source,ROOT/'tools/md_lab.py',ROOT/'build/md_commands.dll',ROOT/'Lion King, The (World).md']
    report=dict(result='OBSERVED',observations=observations,ordinary_prefatal_snapshot=True,guest_or_rom_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
