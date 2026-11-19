"""Bind the original MD caption task and complete ROM picture to displayed SAT."""
import csv
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from md_replay_movie import movie_inputs


def main():
    out=ROOT/'build/pride-title-original2';out.mkdir()
    source=ROOT/'tools/md_title_trace.c';library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-shared','-O2','-static-libgcc',str(source),'-o',str(library)],check=True)
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as f:polled=[pads[int(r['frame'])-1] for r in csv.DictReader(f) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
    trace=C.CDLL(str(library));trace.title_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.title_init(game.core._handle,str(out/'calls.csv').encode())
    index=0;observations=[]
    try:
        for field in range(1,1701):
            trace.title_field(field);game.step(polled[index])
            if trace.title_polled():index+=1
            if field not in (1287,1320,1360,1400,1420,1440,1460):continue
            folder=out/str(field);folder.mkdir();png(folder/'screen.png',*game.image)
            for name in ('work_ram','vram','cram','reg'):(folder/(name+'.bin')).write_bytes(bytes(getattr(game,name)))
            observations.append(field)
    finally:trace.title_close();game.close()
    rows=list(csv.DictReader((out/'calls.csv').open()))
    active=[r for r in rows if r['level']=='1']
    assert active and {r['pose'] for r in active}=={'1d5dac'}
    assert all(r['descriptor']=='1d65ec' and r['x']==r['y']=='0' and int(r['flags'],16)&0x40 for r in active)
    timers=[int(r['timer']) for r in active];assert timers==list(range(100)),timers
    paths=[Path(__file__),source,library,movie,reference,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',
           ROOT/'Lion King, The (World).md',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='ORIGINAL_CAPTION_TASK_VERIFIED',executed_callbacks=len(active),
                first_field=int(active[0]['field']),last_field=int(active[-1]['field']),
                actor=active[0]['actor'],descriptor='1d65ec',callback='1d65f2',pose='1d5dac',
                original_lifetime_updates=100,ordinary_input_no_guest_edits=True,
                captures=observations,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(active),'updates, fields',report['first_field'],report['last_field'],flush=True)


if __name__=='__main__':main()
