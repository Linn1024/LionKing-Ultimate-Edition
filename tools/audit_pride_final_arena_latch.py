"""Observe the original arena's final pending display update without guest writes."""
import ctypes as C
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,MdLab,png
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-final-arena-original';source=base/'report.json';report=bound(source)
    out=base/'latch';out.mkdir();fatal=report['fatal_field'];pads=json.loads((base/'inputs.json').read_text())
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    rows=[]
    try:
        for field,pad in enumerate(pads[:fatal+2],1):
            game.step(pad);game.samples.clear()
            if field<fatal-1:continue
            for name in ('work_ram','vram','cram','reg','vsram'):(out/f'{field-fatal}-{name}.bin').write_bytes(bytes(getattr(game,name)))
            png(out/f'{field-fatal}.png',*game.image)
            word=lambda data,a:struct.unpack_from('<H',bytes(data),a)[0]
            camera=word(game.work_ram,0xcd36);hbase=(game.reg[13]&63)<<10
            rows.append(dict(age=field-fatal,camera=[word(game.work_ram,camera+8),word(game.work_ram,camera+10)],
                background_camera=[word(game.work_ram,0x880c),word(game.work_ram,0x880e)],
                horizontal_scroll=[word(game.vram,hbase),word(game.vram,hbase+2)],
                vertical_scroll=[word(game.vsram,0),word(game.vsram,2)]))
    finally:game.close()
    paths=[Path(__file__),source,base/'inputs.json',ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    result=dict(result='OBSERVED',rows=rows,guest_or_rom_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(rows,flush=True)


if __name__=='__main__':main()
