"""Establish the native scene-clear effect on a future selectable RNG lifecycle.

Research fixtures execute original instructions; no production seed override.
"""
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    root=ROOT/'build/pride-lizard-history';out=root/'rng-clear3';out.mkdir()
    rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    library=root/'rng_clear.dll';core=C.CDLL(str(library));core.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    core.rng_native_clear.argtypes=[C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)];assert core.terrain_native_init(rom,len(rom))
    samples=[];result=(C.c_uint*5)()
    for seed in (0,1,0xffffff,0xa35757,0xa35700,0x9f285a,0x60f4a8,0xa6ba04):
        for checkpoint in (0,1,0xffff):
            for m8 in (0,1):
                assert core.rng_native_clear(seed,checkpoint,m8,result)
                expected=seed&0xffff00 if not checkpoint and not m8 else seed
                assert result[0]==expected and result[2]==m8,(seed,checkpoint,m8,list(result))
                samples.append(dict(seed=seed,checkpoint=checkpoint,m8=m8,after=result[0],steps=result[3]))
    paths=[Path(__file__),ROOT/'tools/pride_rng_clear_oracle.c',ROOT/'tools/pride_terrain_native_oracle.c',library,ROOT/'engine/build-win/tlk-runtime/interp816.c',ROOT/'engine/snesrecomp/runner/src/snes/interp816.c']
    report=dict(result='PASS',fixtures=samples,cases=len(samples),native_scene_clear_can_zero_low_rng_byte=True,
        naive_boot_seed_replacement_does_not_preserve_md_seed=True,production_rng_override_enabled=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(len(samples),'original scene-clear fixtures PASS',flush=True)


if __name__=='__main__':main()
