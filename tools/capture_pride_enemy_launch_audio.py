"""Capture the original NPC FM123 event without assigning it to Simba's sound leaf."""
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


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-enemy-launch-audio';out.mkdir()
    source=ROOT/'tools/md_enemy_launch_audio_trace.c';library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)],cwd=ROOT,check=True)
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv';pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();device=513 if settings['o']['UseSixButton'] else 257
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,device)
    trace=C.CDLL(str(library));trace.enemy_launch_audio_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.enemy_launch_audio_init(game.core._handle,str(out/'events.csv').encode())
    index=0
    try:
        for field in range(1,2835):
            trace.enemy_launch_audio_field(field);game.step(polled[index]);game.samples.clear()
            if trace.enemy_launch_audio_polled():index+=1
            if field in (2570,2571,2572,2832,2833,2834):
                (out/f'wram-{field}.bin').write_bytes(bytes(game.work_ram));png(out/f'client-{field}.png',*game.image)
    finally:trace.enemy_launch_audio_close();game.close()
    events=list(csv.DictReader((out/'events.csv').open()));assert [int(r['field']) for r in events]==[2571,2833]
    paths=[Path(__file__),source,library,movie,reference,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',
           ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='ORIGINAL_NPC_LAUNCH_SOUND_CAPTURED',events=events,original_driver_command=[2,123],
        ordinary_input_no_guest_edits=True,native_equivalence_proven=False,production_mapping_for_this_caller_enabled=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],events,flush=True)


if __name__=='__main__':main()
