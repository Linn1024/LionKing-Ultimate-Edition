"""Capture the original ordinary idle response at its observed installer update."""
import csv
import ctypes as C
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from md_lab import MdLab,png


def main():
    out=ROOT/'build/md-porcupine-idle-response-view2';out.mkdir()
    source=ROOT/'build/md-porcupine-idle-roar2/report.json';original=bound(source)
    tape=source.parent/'3280-56/polled.libretro.tape';data=tape.read_bytes()
    pads=struct.unpack('<'+'H'*(len(data)//2),data)
    library=source.parent/'trace.dll';trace=C.CDLL(str(library));trace.contact_trace_init.argtypes=[C.c_void_p,C.c_char_p]
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    assert trace.contact_trace_init(game.core._handle,str(out/'calls.csv').encode())
    def word(at):return game.work_ram[at]|game.work_ram[at+1]<<8
    def ptr(at):return (word(at)<<16|word(at+2))&0xffffff
    index=0;entry={}
    try:
        for field in range(1,3355):
            trace.contact_trace_field(field);game.step(pads[index])
            if trace.contact_trace_polled():index+=1
            if field==3352:
                png(out/'response-entry.png',*game.image)
                entry=dict(action=hex(ptr(0x9a4e+0x30)),script=hex(ptr(0x9a4e+0xe)),timer=word(0x9a4e+0x2c),
                    wait=word(0x9a4e+0x2e),persistent=word(0x9a4e+0x22),roar_active=word(0xccf4))
            if field==3354:png(out/'response-following.png',*game.image)
    finally:trace.contact_trace_close();game.close()
    rows=list(csv.DictReader((out/'calls.csv').open()))
    installed=[r for r in rows if r['pc']=='19a07e']
    checks=dict(original_observation_reproduced=installed==original['cases']['3280-56']['installed'],
        original_installer_fields=entry==dict(action='0x19a446',script='0xb8acc',timer=28,wait=0,persistent=1,roar_active=24))
    paths=[Path(__file__),source,tape,library,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,entry=entry,
        ordinary_poweron_inputs=True,guest_rom_or_rng_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,entry,flush=True)


if __name__=='__main__':main()
