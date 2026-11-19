"""Observe original cub contact helpers and their pictures; no gameplay edits.

Run with the32-bit research Python. Sound-number equality alone is insufficient
to classify these events as falling-leaf sounds.
"""
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from md_lab import MdLab,png
from md_replay_movie import movie_inputs


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-cub-contact-audio';out.mkdir()
    source=ROOT/'tools/md_cub_contact_audio_trace.c';library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)],check=True,cwd=ROOT)
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();device=513 if settings['o']['UseSixButton'] else 257
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,device)
    trace=C.CDLL(str(library));trace.md_contact_audio_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_contact_audio_init(game.core._handle,str(out/'entries.csv').encode())
    w=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
    addr=lambda at:w(at)<<16|w(at+2)
    index=0;last_event=0;observations=[]
    try:
        for field in range(1,4355):
            trace.md_contact_audio_field(field);game.step(polled[index]);game.samples.clear()
            if trace.md_contact_audio_polled():index+=1
            if trace.md_contact_audio_events():last_event=field
            # Include pre-event fields from the independent sound census.
            if (last_event and field<=last_event+5) or field in (1873,2702,4190):
                actor=0x93ce
                observations.append(dict(field=field,action=f'{addr(actor+0x30):06x}',
                    x=w(actor+8),y=w(actor+10),vx=addr(actor+0x38),vy=addr(actor+0x3c),
                    timer=w(actor+0x2c),level=w(0xccce)))
                (out/f'wram-{field}.bin').write_bytes(bytes(game.work_ram))
                png(out/f'client-{field}.png',*game.image)
    finally:trace.md_contact_audio_close();game.close()
    entries=list(csv.DictReader((out/'entries.csv').open()))
    assert [int(r['field']) for r in entries]==[1874,2703,4191],entries
    assert all(r['level']=='0001' for r in entries)
    paths=[Path(__file__),source,library,movie,reference,ROOT/'tools/md_lab.py',
           ROOT/'tools/md_replay_movie.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='ORIGINAL_CONTACT_AUDIO_ENTRIES_CAPTURED',entries=entries,observations=observations,
        original_rom_or_guest_mutations=False,production_sound_mapping_enabled=False,
        semantic_equivalence_with_native_proven=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],entries,flush=True)


if __name__=='__main__':main()
