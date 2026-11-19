"""Original ordinary-input attack lifetimes and sound-phase entry captures."""
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
    out=ROOT/'build/md-porcupine-attack';out.mkdir()
    source=ROOT/'tools/md_porcupine_attack_trace.c';library=out/'trace.dll'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)]
    subprocess.run(command,check=True,cwd=ROOT)
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        inputs=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();device=513 if settings['o']['UseSixButton'] else 257
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,device)
    trace=C.CDLL(str(library));trace.attack_trace_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.attack_trace_init(game.core._handle,str(out/'calls.csv').encode())
    index=0;captures=[]
    try:
        for field in range(1,3501):
            trace.attack_trace_field(field);game.step(inputs[index])
            if trace.attack_trace_polled():index+=1
            if trace.attack_trace_sound():
                path=out/f'sound-{field}.png';png(path,*game.image)
                captures.append(dict(field=field,path=path.name))
    finally:trace.attack_trace_close();game.close()
    rows=list(csv.DictReader((out/'calls.csv').open()))
    sound=[r for r in rows if r['pc']=='19a594']
    checks=dict(attack_executed=any(r['pc']=='19a446' and r['action']=='19a446' for r in rows),
                sound_executed=bool(sound),sound_only_at28=bool(sound) and all(r['timer']=='28' for r in sound),
                sound_only_persistent=bool(sound) and all(int(r['persistent'])!=0 for r in sound),
                sound_on_pride=bool(sound) and all(r['level']=='1' for r in sound))
    paths=[Path(__file__),source,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',
           ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',movie,reference]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,compile_command=command,
                calls=len(rows),sound_calls=sound,captures=captures,controller_polls=index,
                ordinary_poweron_inputs=True,guest_or_rom_edits=False,runtime_adapter_enabled=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(rows),'calls',len(sound),'sound phases',flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
