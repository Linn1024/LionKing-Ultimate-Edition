"""Measure real post-Continue movement readiness in the original MD game."""
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png


def main():
    out=ROOT/'build/pride-continue-control-reference';out.mkdir()
    origin=ROOT/'build/pride-final-input-reference/prefatal.state';raw=origin.read_bytes();state=C.create_string_buffer(raw)
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    cases={}
    try:
        for confirm in (124,130):
            assert game.core.retro_unserialize(state,len(raw));rows=[];first=None
            for age in range(461):
                game.step(128 if age==0 or age>=380 else (256 if age==confirm else 0));game.samples.clear()
                word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                camera=word(0xcd36);player=word(camera+0x24) if 0x8000<=camera<0xffc8 else 0
                if age>300 and word(0xccf6)==6 and 0x8000<=player<0xffc0:
                    x,y=word(player+8),word(player+10);rows.append(dict(age=age,x=x,y=y))
                    if x>65 and first is None:first=age;png(out/f'{confirm}-first-movement.png',*game.image)
            cases[str(confirm)]=dict(first_movement=first,rows=rows)
            print('MD confirm',confirm,'first movement',first,flush=True)
    finally:game.close()
    paths=[Path(__file__),origin,ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md']
    report=dict(result='OBSERVED',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
