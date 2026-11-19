"""Capture original final-menu initialization, planes and sprite submissions.

Uses ordinary original inputs or an established ordinary prefatal checkpoint;
never edits guest or ROM memory. Game-derived output stays under build/.
Run with the pinned 32-bit Python used by md_lab.
"""
import ctypes as C
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,MdLab,png
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-final-menu-art-original';out.mkdir()
    normal=ROOT/'build/pride-final-input-reference/report.json';bound(normal)
    arena=ROOT/'build/pride-final-arena-original/report.json';old=bound(arena)
    checkpoint=normal.parent/'prefatal.state';inputs=arena.parent/'inputs.json'
    pads=json.loads(inputs.read_text());game=MdLab();observations={}
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    samples={90,96,97,100,118,120,124,125,140,141,160,180,200,220}
    try:
        for case in ('continue','game-over'):
            folder=out/case;folder.mkdir();rows=[]
            if case=='continue':
                data=checkpoint.read_bytes();blob=C.create_string_buffer(data)
                assert game.core.retro_unserialize(blob,len(data))
            else:
                game.close();game=MdLab()
                game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
                for port in (0,1):game.core.retro_set_controller_port_device(port,513)
                for pad in pads[:old['fatal_field']-1]:game.step(pad);game.samples.clear()
            for age in range(221):
                game.step(128 if case=='continue' and age==0 else
                          (pads[old['fatal_field']-1] if case=='game-over' and age==0 else 0))
                game.samples.clear()
                if age<90:continue
                word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                reg=bytes(game.reg);vram=bytes(game.vram);sat=(reg[5]&0x7e)<<9
                sprites=[];index=0;seen=set()
                while index not in seen and len(sprites)<80:
                    seen.add(index);at=(sat+index*8)&65535
                    words=[vram[at+n]|vram[at+n+1]<<8 for n in range(0,8,2)]
                    sprites.append(dict(index=index,words=words));index=words[1]&127
                    if not index:break
                rows.append(dict(age=age,level=word(0xccce),lives=word(0xccee),
                    registers=list(reg),sprites=sprites,vram_sha256=__import__('hashlib').sha256(vram).hexdigest(),
                    cram_sha256=__import__('hashlib').sha256(bytes(game.cram)).hexdigest()))
                if age in samples:
                    target=folder/str(age);target.mkdir();png(target/'window.png',*game.image)
                    for name in ('work_ram','vram','cram','reg','vsram'):
                        (target/(name+'.bin')).write_bytes(bytes(getattr(game,name)))
            observations[case]=rows
    finally:game.close()
    paths=[Path(__file__),normal,arena,checkpoint,inputs,ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md']
    report=dict(result='CAPTURED',observations=observations,guest_or_rom_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Captured original Continue and Game Over planes/initialization/sprites',flush=True)


if __name__=='__main__':main()
