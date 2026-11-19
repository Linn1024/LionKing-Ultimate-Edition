"""Observe original active actors from ordinary boot to the missed stomp.

Run with the32-bit research Python; observations do not alter original state.
"""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))

from md_lab import MdLab,ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-lizard-history/md';out.mkdir(parents=True)
    source=ROOT/'build/md-next-levels-replay/frames.json';original=json.loads(source.read_text())
    game=MdLab();library=ROOT/'build/pride-lizard-history/md_spawn_trace.dll';trace=C.CDLL(str(library))
    trace.md_spawn_trace_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_spawn_trace_init(game.core._handle,str(out/'spawns.csv').encode())
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    game.core.retro_set_controller_port_device(0,513);game.core.retro_set_controller_port_device(1,513)
    rows=[]
    def word(at):return game.work_ram[at]|game.work_ram[at+1]<<8
    try:
        for row in original[:2017]:
            trace.md_spawn_trace_frame(row['frame']);game.step(row['pad']);game.samples.clear()
            if row['level']!=0 or row['player'] is None:continue
            assert [word(0x93d6),word(0x93d8)]==row['player']
            actors=[];at=word(0x9350);previous=0x934e
            while at:
                assert at>=0x8000 and at+128<=65536 and len(actors)<80 and word(at)==previous,(row['frame'],at)
                values=[word(at+2*n) for n in range(64)]
                actors.append(dict(actor=at,words=values))
                previous,at=at,values[1]
            rows.append(dict(field=row['frame'],poll=row['poll'],pad=row['pad'],player=row['player'],actors=actors))
    finally:trace.md_spawn_trace_close();game.close()
    path=out/'actors.json';path.write_text(json.dumps(rows,separators=(',',':'))+'\n')
    paths=[Path(__file__),source,ROOT/'tools/md_lab.py',ROOT/'tools/md_spawn_trace.c',library,ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='CAPTURED',fields=len(rows),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'},original_game_mutated=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Captured',len(rows),'original active-list fields',flush=True)


if __name__=='__main__':main()
