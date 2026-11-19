"""Capture an ordinary original MD hard last-life hyena hit and all fade fields."""
import ctypes as C
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,MdLab,png
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    source=ROOT/'build/pride-hyena-hits/md/report.json';bound(source)
    inputs=ROOT/'build/pride-hyena-hits/md/hard/inputs.json';prefix=json.loads(inputs.read_text())[:4100]
    out=ROOT/'build/pride-final-arena-original';out.mkdir();game=MdLab()
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    pads=[];fatal=None;previous=1;initial=None;captures=[]
    try:
        for field in range(1,9001):
            pad=prefix[field-1] if field<=len(prefix) else (64 if ((field-4101)//24)%2==0 else 128)
            if fatal is not None:pad=0
            pads.append(pad);game.step(pad);game.samples.clear()
            word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
            if field==4100:
                initial=dict(level=word(0xccce),health=word(0xccf6),lives=word(0xccee),
                    player=[word(0x93d6),word(0x93d8)],boss_health=word(0x9a4e+0x2a))
                assert initial['level']==1 and initial['lives']==1 and initial['boss_health']==2
            lives=word(0xccee)
            if field>4100 and previous==1 and lives==0:
                assert word(0xccf6)==0 and word(0xccce)==1
                fatal=field
                for name in ('work_ram','vram','cram','reg','vsram'):
                    (out/('fatal-'+name+'.bin')).write_bytes(bytes(getattr(game,name)))
            previous=lives
            if fatal is not None:
                age=field-fatal;png(out/f'final-{age:03d}.png',*game.image)
                (out/f'final-{age:03d}-wram.bin').write_bytes(bytes(game.work_ram))
                captures.append(dict(age=age,health=word(0xccf6),lives=lives))
                if age==120:break
    finally:game.close()
    assert fatal is not None and len(captures)==121
    (out/'inputs.json').write_text(json.dumps(pads)+'\n')
    paths=[Path(__file__),source,inputs,ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md',
        ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='CAPTURED',ordinary_power_on=True,guest_or_rom_edits=False,loaded_states=False,
        initial_arena=initial,fatal_field=fatal,captures=captures,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Original MD arena last life',fatal,flush=True)


if __name__=='__main__':main()
