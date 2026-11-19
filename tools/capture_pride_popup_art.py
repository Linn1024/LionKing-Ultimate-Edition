"""Capture original MD HUD arrival artwork on ordinary, credited movie input.

Read-only observer. Assets and captures stay under ignored build/. Memory
samples are distinguished from actual executed callbacks in calls.csv.
"""
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from md_lab import MdLab, png
from md_replay_movie import movie_inputs


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'build/pride-popup-original'
    out.mkdir()
    observer = ROOT/'tools/md_pickup_flight_trace.c'
    trace_source = out/'trace.c'
    original = '(address!=0x18f6a2 && address!=0x18f87e)'
    source = observer.read_text()
    assert source.count(original) == 1
    trace_source.write_text(source.replace(original,
        '(address!=0x18ffe6 && address!=0x190048)'))
    library = out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe', '-O2', '-shared', '-static-libgcc',
                    str(trace_source), '-o', str(library)], check=True)
    movie = ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference = ROOT/'build/md-next-levels-reference/ram.csv'
    pads, _, settings = movie_inputs(movie)
    with reference.open() as stream:
        polled = [pads[int(r['frame'])-1] for r in csv.DictReader(stream)
                  if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game = MdLab()
    device = 513 if settings['o']['UseSixButton'] else 257
    game.core.retro_set_controller_port_device.argtypes = [C.c_uint, C.c_uint]
    for port in (0, 1):
        game.core.retro_set_controller_port_device(port, device)
    trace = C.CDLL(str(library))
    trace.pickup_flight_init.argtypes = [C.c_void_p, C.c_char_p]
    assert trace.pickup_flight_init(game.core._handle, str(out/'calls.csv').encode())
    def word(at):
        return game.work_ram[at] | game.work_ram[at+1]<<8
    def address(at):
        return (word(at)<<16 | word(at+2)) & 0xffffff
    index = 0
    samples = []
    try:
        for field in range(1, 2251):
            trace.pickup_flight_field(field)
            game.step(polled[index])
            if trace.pickup_flight_polled():
                index += 1
            if word(0xccce) != 1:
                continue
            for actor in range(0x944e, 0xa3ce, 0x80):
                if address(actor+0x30) != 0x18ffe6:
                    continue
                draw = word(actor+12)
                if not 0x8000<=draw<=0xffe0:
                    continue
                row = dict(field=field, actor=actor, draw=draw,
                           pose=address(draw+10), flags=word(draw+8),
                           timer=word(actor+0x2c), x=word(actor+8), y=word(actor+10))
                samples.append(row)
                # Every active frame: the complete short transition can be reviewed.
                png(out/f'popup-{field}.png', *game.image)
                (out/f'cram-{field}.bin').write_bytes(bytes(game.cram))
    finally:
        trace.pickup_flight_close()
        game.close()
    calls = list(csv.DictReader((out/'calls.csv').open()))
    assert samples and any(r['callback']=='190048' for r in calls)
    paths = [Path(__file__), observer, movie, reference, ROOT/'tools/md_lab.py',
             ROOT/'tools/md_replay_movie.py', ROOT/'Lion King, The (World).md',
             ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report = dict(result='ORIGINAL_POPUP_ART_CAPTURED', samples=samples,
                  executed_callbacks=len(calls), input_polls=index,
                  ordinary_input_no_guest_edits=True,
                  complete_artwork_mapping=False,
                  source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                  artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], len(samples), 'active fields;',
          sorted({hex(r['pose']) for r in samples}), flush=True)


if __name__=='__main__':
    main()
