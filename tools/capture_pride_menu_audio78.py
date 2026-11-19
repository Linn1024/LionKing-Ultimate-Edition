"""Read-only menu pictures at original MD sound calls; preserve title77 capture."""
import csv
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from md_replay_movie import movie_inputs
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-title-audio77/report.json';p=bound(prior)
    assert p['result']=='ORIGINAL_TITLE_CAPTURED' and all(p['checks'].values())
    out=ROOT/'build/pride-menu-audio78';out.mkdir()
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
    library=ROOT/'build/pride-audio-inventory/trace.dll';trace=C.CDLL(str(library))
    trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_commands_init(game.core._handle,str(out/'commands.csv').encode())
    inputs=[];index=0
    try:
        for field in range(1,1101):
            pad=polled[index];trace.md_commands_frame(field);game.step(pad);game.samples.clear()
            if trace.md_commands_polled():index+=1
            inputs.append(dict(field=field,pad=pad,poll_index=index))
            if field in (900,950,975,985,990,995,999,1000,1004,1010,1020,1029,1100):png(out/f'{field}.png',*game.image)
    finally:trace.md_commands_close();game.close()
    calls=list(csv.DictReader((out/'commands.csv').open()))
    checks=dict(all1100_original_commands_exact=calls==[r for r in p['observations']['route']['calls'] if int(r['frame'])<=1100],
                title950_picture_exact=digest(out/'950.png')==digest(prior.parent/'route/950.png'))
    paths=[Path(__file__),prior,movie,reference,library,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py']
    report=dict(result='MENU_CALL_PICTURES_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,inputs=inputs,
                ordinary_inputs=True,guest_or_rom_edits=False,source_mapping_proven=False,
                source_sha256={path.relative_to(ROOT).as_posix():digest(path) for path in paths},
                artifacts_sha256={path.relative_to(out).as_posix():digest(path) for path in out.rglob('*') if path.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
