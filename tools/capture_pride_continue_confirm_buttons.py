"""Observe original Continue confirmation outcomes through the complete reload."""
import ctypes as C
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png


def main():
    out=ROOT/'build/pride-continue-confirm-buttons';out.mkdir()
    origin=ROOT/'build/pride-final-input-reference/prefatal.state';raw=origin.read_bytes()
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    state=C.create_string_buffer(raw)
    trace=C.CDLL(str(ROOT/'build/md_commands.dll'));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    cases={}
    try:
        for name,button in [('a',2),('b',1),('c',256),('start',8)]:
            folder=out/name;folder.mkdir();assert game.core.retro_unserialize(state,len(raw))
            assert trace.md_commands_init(game.core._handle,str(folder/'commands.csv').encode())
            restored=None;observed=[]
            for age in range(1001):
                pad=128 if age==0 else (64 if 150<=age<=156 else (button if 160<=age<=163 else 0))
                trace.md_commands_frame(14788+age);game.step(pad);game.samples.clear()
                word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                if age>1 and word(0xccf6) and restored is None:restored=age
                if age in (120,180,240,400,800,1000):
                    png(folder/f'{age}.png',*game.image);(folder/f'{age}-wram.bin').write_bytes(bytes(game.work_ram))
                    observed.append(dict(age=age,health=word(0xccf6),lives=word(0xccee),level=word(0xccce)))
            trace.md_commands_close()
            events=list(csv.DictReader((folder/'commands.csv').open()))
            music=[dict(age=int(r['frame'])-14788,value=int(r['value']),caller=r['caller']) for r in events if r['selector']=='1']
            cases[name]=dict(first_health=restored,music=music,observations=observed)
            print(name,'health',restored,'music',music,flush=True)
    finally:game.close()
    paths=[Path(__file__),origin,ROOT/'tools/md_lab.py',ROOT/'build/md_commands.dll',ROOT/'Lion King, The (World).md']
    report=dict(result='OBSERVED',cases=cases,guest_or_rom_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
