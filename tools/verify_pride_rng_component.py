"""Compare original clear paths with the uninstalled owned RNG component."""
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-rng-lifecycle';out=base/'component2';out.mkdir()
    library=base/'rng_policy_oracle.dll';core=C.CDLL(str(library))
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    core.terrain_native_init.argtypes=[C.c_void_p,C.c_uint];assert core.terrain_native_init(snes,len(snes))
    core.rng_scene_original.argtypes=[C.c_uint]*6+[C.c_void_p,C.c_uint,C.POINTER(C.c_uint),C.c_void_p]
    result=(C.c_uint*4)();after=C.create_string_buffer(0x20000);cases=[]
    for seed in (0,0xffffff,0x9f285a,0xa35757,0x697bf5,0x90a99c):
        for checkpoint in (0,1):
            for m8 in (0,1):
                for descriptor in (0,0xc00387,0xc0080d,0xc005ab):
                    assert core.rng_scene_original(seed,checkpoint,m8,descriptor,0,0,md,len(md),result,after)
                    original=after.raw;expected=int.from_bytes(original[0x1e00:0x1e03],'little')
                    if not checkpoint and not m8:
                        if not descriptor:expected=0xaa0b4c
                        elif descriptor in (0xc00387,0xc0080d):expected=seed
                    for fresh in (0,1):
                        assert core.rng_scene_original(seed,checkpoint,m8,descriptor,1,fresh,md,len(md),result,after)
                        assert result[0]==expected and result[1]==checkpoint and result[2]==m8
                        # Every byte outside the three seed bytes equals the
                        # unchanged original, including saved status/stack.
                        assert after.raw[:0x1e00]==original[:0x1e00] and after.raw[0x1e03:]==original[0x1e03:]
                        if fresh and not checkpoint:assert result[3]==1
                        cases.append(dict(seed=seed,checkpoint=checkpoint,m8=m8,descriptor=descriptor,fresh=fresh,after=result[0]))
    (out/'cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
    paths=[Path(__file__),ROOT/'tools/pride_rng_policy_oracle.c',ROOT/'tools/pride_terrain_native_oracle.c',ROOT/'engine/runner/tlk_rng_scene.c',ROOT/'engine/runner/tlk_rng_scene.h',library,ROOT/'engine/build-win/tlk-runtime/interp816.c',ROOT/'engine/snesrecomp/runner/src/snes/interp816.h']
    report=dict(result='PASS',original_instruction_cases=len(cases),fresh_post_stz_context=True,all_nonseed_ram_unchanged=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'cases.json':digest(out/'cases.json')},
        component_installed=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(len(cases),'original-instruction RNG policy cases PASS; component not installed',flush=True)


if __name__=='__main__':main()
