"""Observe original MD motion at the first remaining controller-aligned gap.

Run with the32-bit research Python. No register, input, ROM or RAM edits.
"""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))

from md_lab import MdLab,ROOT,png
from audit_scenes import read_rom


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-ground-gap/md';out.mkdir()
    source=ROOT/'build/md-next-levels-replay/frames.json';rows=json.loads(source.read_text())
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    game=MdLab();trace=C.CDLL(str(ROOT/'build/pride-ground-gap/md_ground_gap_trace.dll'))
    trace.md_ground_gap_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_ground_gap_init(game.core._handle,str(out/'instructions.csv').encode())
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    game.core.retro_set_controller_port_device(0,513);game.core.retro_set_controller_port_device(1,513)
    w=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
    captures=[]
    try:
        for row in rows[:2017]:
            trace.md_ground_gap_field(row['frame']);game.step(row['pad']);game.samples.clear()
            if row['frame']>=2012:
                assert [w(0x93d6),w(0x93d8)]==row['player'],row['frame']
                path=out/f"wram-{row['frame']}.bin";path.write_bytes(bytes(game.work_ram))
                png(out/f"client-{row['frame']}.png",*game.image)
                captures.append(dict(field=row['frame'],pad=row['pad'],player=row['player'],health=w(0xccf6),
                    vx=w(0x9406)<<16|w(0x9408),vy=w(0x940a)<<16|w(0x940c),state=w(0x93fe)<<16|w(0x9400),
                    contact=w(0x93f2)<<16|w(0x93f4),flags=w(0x9416),input=w(0xccba),edges=w(0xccbc)))
    finally:trace.md_ground_gap_close();game.close()
    paths=[Path(__file__),ROOT/'tools/md_ground_gap_trace.c',ROOT/'build/pride-ground-gap/md_ground_gap_trace.dll',source,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='CAPTURED',scope=__doc__,frames=captures,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'},
        original_rom_or_guest_mutations=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(captures),flush=True)


if __name__=='__main__':main()
