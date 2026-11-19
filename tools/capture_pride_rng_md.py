"""Observe original MD RNG through completion, checkpoint death and Continue YES.

Ordinary controller inputs from power-on; no register/RAM/ROM or seed edits.
Run with embedded32-bit Python and the read-only RNG trace DLL.
"""
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))

from md_lab import MdLab,ROOT,png
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-rng-lifecycle';out=base/'md';out.mkdir();source=ROOT/'build/md-next-levels-replay/frames.json';original=json.loads(source.read_text());paths=[Path(__file__),source]
    library=base/'md_rng_trace.dll';trace=C.CDLL(str(library));trace.md_rng_lifecycle_init.argtypes=[C.c_void_p,C.c_char_p];cases={}
    for name,end in (('completion',6000),('checkpoint',5400),('continue',16000)):
        folder=out/name;folder.mkdir();game=MdLab();assert trace.md_rng_lifecycle_init(game.core._handle,str(folder/'rng.csv').encode())
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513)
        def word(a):return game.work_ram[a]|game.work_ram[a+1]<<8
        def seed():return sum(game.work_ram[a^1]<<shift for a,shift in ((0x81af,0),(0x81ae,8),(0x81ad,16)))
        records=[];last=None;validated=0
        try:
            for field in range(1,end+1):
                if name=='completion':pad=original[field-1]['pad']
                elif field<=4000:pad=original[field-1]['pad']
                elif name=='checkpoint' or field<=5400:pad=0
                elif field<=15300:pad=128
                elif field<=15310:pad=64
                elif 15320<=field<=15322:pad=2
                else:pad=0
                trace.md_rng_lifecycle_field(field);game.step(pad);game.samples.clear()
                if name=='completion' or field<=4000:
                    expected=original[field-1]
                    if expected['player'] is not None:assert [word(0x93d6),word(0x93d8)]==expected['player'];validated+=1
                state=(word(0xccce),word(0xccf6),word(0xccee),word(0xccd6)<<16|word(0xccd8))
                if state!=last or field in (1,15315,15325,end):
                    records.append(dict(field=field,pad=pad,seed=seed(),level=state[0],health=state[1],lives=state[2],checkpoint=state[3]));last=state
                if field in (15300,15315,end):png(folder/f'client-{field}.png',*game.image)
        finally:trace.md_rng_lifecycle_close();game.close()
        (folder/'milestones.json').write_text(json.dumps(records,indent=2)+'\n')
        cases[name]=dict(fields=end,original_player_samples_match=validated,final=records[-1]);print(name,records[-1],flush=True)
    paths.extend([ROOT/'tools/md_rng_lifecycle_trace.c',library,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'])
    report=dict(result='CAPTURED',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},ordinary_poweron_controller_inputs_only=True,game_mutated=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
