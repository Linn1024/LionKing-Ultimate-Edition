"""Reach original MD last-life transition through a controller-only Options change."""
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png


def main():
    out=ROOT/'build/pride-hard-final-reference';out.mkdir()
    source=ROOT/'build/md-next-levels-replay/frames.json';inputs=json.loads(source.read_text())
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    loss=[];previous=None;fatal=None;initial=None;captures=[]
    try:
        for field in range(1,20001):
            pad=inputs[field-1]['pad'] if field<=1400 else 0
            if field==1000:pad=128  # Right in Options, replacing recorded Left.
            game.step(pad);game.samples.clear()
            word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
            if field in (1000,1400):png(out/f'{field}.png',*game.image)
            if field==1400:initial=dict(health=word(0xccf6),lives=word(0xccee),level=word(0xccce))
            if field>=1400 and word(0xccce)==1:
                lives=word(0xccee)
                if previous is not None and lives<previous:
                    loss.append(dict(field=field,before=previous,after=lives,health=word(0xccf6)))
                    if not lives:fatal=field
                previous=lives
            if fatal is not None and field<=fatal+120:
                offset=field-fatal;png(out/f'final-{offset:03d}.png',*game.image)
                (out/f'final-{offset:03d}-wram.bin').write_bytes(bytes(game.work_ram))
                captures.append(dict(offset=offset,health=word(0xccf6),lives=word(0xccee)))
            if fatal is not None and field==fatal+120:break
    finally:game.close()
    assert fatal is not None and initial is not None
    paths=[Path(__file__),source,ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='CAPTURED',ordinary_options_right_at_1000=True,loaded_states=False,guest_or_rom_edits=False,
        initial=initial,life_losses=loss,fatal_field=fatal,captures=captures,
        difficulty_name_requires_menu_inspection=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original Options variant',initial,'final',fatal,'life losses',loss,flush=True)


if __name__=='__main__':main()
