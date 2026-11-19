"""Observe the actual sound-driver dispatch from a genuine Sun contact branch."""
import csv
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from md_lab import MdLab,png
from md_replay_movie import movie_inputs
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    contact=ROOT/'build/md-continue-token-contact/report.json';assert bound(contact)['result']=='PASS'
    out=ROOT/'build/md-continue-token-driver';out.mkdir();source=ROOT/'tools/md_commands.c';library=out/'trace.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)],check=True)
    game=MdLab();trace=C.CDLL(str(library));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2';_,_,settings=movie_inputs(movie)
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
    seed=contact.parent/'seed.state';state=C.create_string_buffer(seed.read_bytes())
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    assert game.core.retro_unserialize(state,len(state)-1)
    assert trace.md_commands_init(game.core._handle,str(out/'commands.csv').encode())
    try:
        for step in range(1,151):trace.md_commands_frame(2743+step);game.step(1<<6 if step<=5 else 0)
        (out/'audio.pcm').write_bytes(game.samples);(out/'final-ram.bin').write_bytes(bytes(game.work_ram));png(out/'final.png',*game.image)
    finally:trace.md_commands_close();game.close()
    rows=list(csv.DictReader((out/'commands.csv').open()));sun=[r for r in rows if r['outer_caller']=='18fd82']
    checks=dict(exactly_one_sun_driver_call=len(sun)==1,
                selector19_pcm15_parameter96=len(sun)==1 and (sun[0]['selector'],sun[0]['value'],sun[0]['parameter'])==('19','15','96'),
                original_actor_and_contact_field=len(sun)==1 and (sun[0]['frame'],sun[0]['actor'],sun[0]['actor_state'])==('2781','9dce','18fd02'),
                not_a_background_music_command=all(r['selector']!='1' for r in sun),
                original_contact_pcm_reproduced=digest(out/'audio.pcm')==digest(contact.parent/'left-5/audio.pcm'))
    paths=[Path(__file__),contact,source,library,seed,movie,ROOT/'tools/md_lab.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,sun_driver_calls=sun,
                earlier_music15_label_incorrect=True,actual_semantics='PCM voice15, parameter96, selector19; 2210 is a PCM wrapper',
                no_guest_memory_or_register_edits=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,sun,flush=True)


if __name__=='__main__':main()
