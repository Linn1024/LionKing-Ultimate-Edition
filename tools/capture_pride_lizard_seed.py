"""Read the original pre-decision RNG state after an unmodified ordinary replay."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-lizard-history/md-seed';out.mkdir()
    source=ROOT/'build/md-next-levels-replay/frames.json';rows=json.loads(source.read_text());game=MdLab()
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    game.core.retro_set_controller_port_device(0,513);game.core.retro_set_controller_port_device(1,513)
    try:
        for row in rows[:1958]:game.step(row['pad']);game.samples.clear()
        raw=bytes(game.work_ram);(out/'wram-1958.bin').write_bytes(raw)
        seed=sum(raw[a^1]<<shift for a,shift in ((0x81af,0),(0x81ae,8),(0x81ad,16)))
        assert seed==0xa6ba04
    finally:game.close()
    paths=[Path(__file__),source,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='CAPTURED',frame=1958,seed=seed,original_game_mutated=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'wram-1958.bin':digest(out/'wram-1958.bin')})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Original live pre-decision seed',hex(seed),flush=True)


if __name__=='__main__':main()
