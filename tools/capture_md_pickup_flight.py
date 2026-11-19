"""Observe original MD pickup flight calls on the ordinary credited All Bugs route.

Read-only CPU hook distinguishes executed actions from stale actor memory.
No renderer mapping or full behavior equivalence is implied by observations.
"""
import argparse
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
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='build/md-pickup-flight')
    args=parser.parse_args();out=(ROOT/args.out).resolve()
    assert out.is_relative_to(ROOT/'build');out.mkdir()
    source=ROOT/'tools/md_pickup_flight_trace.c';library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)],check=True)
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();device=513 if settings['o']['UseSixButton'] else 257
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,device)
    trace=C.CDLL(str(library));trace.pickup_flight_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.pickup_flight_init(game.core._handle,str(out/'calls.csv').encode())
    index=0;captures=[];previous=set()
    def w(at):return game.work_ram[at]|game.work_ram[at+1]<<8
    def addr(at):return (w(at)<<16|w(at+2))&0xffffff
    try:
        for field in range(1,3501):
            trace.pickup_flight_field(field);game.step(polled[index])
            if trace.pickup_flight_polled():index+=1
            present=set()
            for actor in range(0x944e,0xa3ce,0x80):
                action=addr(actor+0x30)
                if action not in (0x18f6a2,0x18f87e) or w(0xccce)!=1:continue
                present.add((actor,action))
                if (actor,action) not in previous:
                    path=out/f'entry-{field}-{actor:x}.png';png(path,*game.image)
                    captures.append(dict(field=field,actor=actor,action=hex(action),path=path.name))
            previous=present
    finally:trace.pickup_flight_close();game.close()
    rows=list(csv.DictReader((out/'calls.csv').open()))
    active=[r for r in rows if r['level']=='1' and r['callback']==r['action'] and int(r['flags'],16)&0x40]
    metadata_path=ROOT/'tools/pride_npc_pairs.json'
    metadata={int(r['md'],16):r for r in json.loads(metadata_path.read_text())['pairs'] if r['role']=='pickup'}
    # Record uncovered poses rather than silently infer artwork correspondences.
    missing=sorted({r['pose'] for r in active if int(r['pose'],16) not in metadata})
    paths=[Path(__file__),source,library,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',
        ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',movie,reference,metadata_path]
    report=dict(result='OBSERVED' if active else 'NO_FLIGHT_OBSERVED',executed_flight_calls=len(rows),
        initialized_fixed_flight_calls=len(active),poses=sorted({r['pose'] for r in active}),
        actions=sorted({r['action'] for r in active}),unreviewed_flight_poses=missing,entries=captures,
        ordinary_input_no_guest_edits=True,production_mappings_unchanged=True,
        memory_only_entries_not_action_execution_proof=True,all_flight_types_verified=False,
        rom_sha256=hashlib.sha256(rom).hexdigest(),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(active),'initialized executed calls; poses',report['poses'],flush=True)


if __name__=='__main__':main()
