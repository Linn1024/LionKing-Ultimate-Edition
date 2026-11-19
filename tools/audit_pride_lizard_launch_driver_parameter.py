"""Compare original FM123 PCM across seven controlled D1 sentinel values."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from md_lab import MdLab


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-lizard-launch-driver-parameter';out.mkdir()
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    game=MdLab();results={}
    try:
        for _ in range(180):game.step()
        core=game.core;core.retro_serialize_size.restype=C.c_size_t
        size=core.retro_serialize_size();state=C.create_string_buffer(size)
        for name in ('retro_serialize','retro_unserialize'):
            fn=getattr(core,name);fn.argtypes=[C.c_void_p,C.c_size_t];fn.restype=C.c_bool
        assert core.retro_serialize(state,size)
        for parameter in (0,1,0x14,0x9f,0x5a,0xcf80,0xffffffff):
            assert core.retro_unserialize(state,size);game.samples.clear()
            core.m68k_set_reg(1,parameter)
            for field in range(120):game.driver_step(2 if field==0 else None,123)
            results[f'{parameter:08x}']=dict(pcm_sha256=hashlib.sha256(game.samples).hexdigest(),pcm_bytes=len(game.samples))
    finally:game.close()
    assert len({(r['pcm_sha256'],r['pcm_bytes']) for r in results.values()})==1
    paths=[Path(__file__),ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='CONTROLLED_FM123_PARAMETERS_PCM_IDENTICAL',parameters=results,
        original_driver_command=[2,123],fields=120,same_serialized_original_start=True,
        controlled_driver_fixture_not_gameplay=True,all_possible_driver_parameter_semantics_proven=False,
        rom_sha256=hashlib.sha256(rom).hexdigest(),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'seven controlled D1 sentinels; not a complete parameter ABI proof',flush=True)


if __name__=='__main__':main()
