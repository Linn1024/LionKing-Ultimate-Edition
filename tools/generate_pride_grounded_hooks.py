"""Generate isolated pre-op hook clones using the existing patched emitter.

Only build/ output is generated. No submodule, production generated source,
configuration, or installed binary is rewritten. This is an experimental
backend extension, not evidence that compiled ownership already works.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import sys
from audit_scenes import ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-grounded/generated';out.mkdir(parents=True,exist_ok=True)
    assert out.resolve().is_relative_to((ROOT/'build').resolve())
    backend=ROOT/'engine/build/snesrecomp-codegen'
    compiler=backend/'recompiler/v2/emit_function.py'
    hook_sources=[ROOT/'tools'/name for name in (
        'pride_grounded_restore.c','pride_grounded_service.h','pride_grounded_owner.c','pride_scene_prepare_probe.c',
        'pride_scene_template.h','pride_native_bank_probe.c')]
    text='\n'.join(p.read_text() for p in hook_sources)
    points={int(v,16) for v in re.findall(r'0x([cC][013][0-9a-fA-F]{4})\b',text)}
    redirects={int(v,16) for v in re.findall(r'interp_bridge_pre_opcode_redirect\(0x([0-9a-fA-F]{6})\)',text)}
    points|=redirects
    rom_path=ROOT/'Lion King, The (USA).sfc';rom=rom_path.read_bytes()
    assert digest(rom_path)=='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    # The decoder observer registers its real JSL return dynamically. Include
    # all source-ROM direct decoder return sites, not a guessed heap/scene PC.
    at=0
    while (at:=rom.find(bytes.fromhex('22feccc1'),at))>=0:
        points.add(0xc00000+at+4);at+=1
    sys.path.insert(0,str(backend/'recompiler'))
    import v2.emit_function as emitter
    source=compiler.read_text()
    marker='    base_func_name = func_name if func_name is not None else _default_func_name(bank, start)'
    assert source.count(marker)==1
    source=source.replace(marker,'    _pride_labels = set()\n'+marker)
    loop='        for ii, (di_insn, ir_ops) in enumerate(pairs):'
    assert source.count(loop)==1
    injection='''
            _pride_pc = getattr(di_insn, 'addr', 0) & 0xffffff
            if _pride_pc in PRIDE_POINTS:
                if ii in skip_emit_idx:
                    raise RuntimeError(('hook intersects synthesized instruction',func_name,hex(_pride_pc)))
                _pride_key = (_pride_pc, int(di_insn.m_flag), int(di_insn.x_flag))
                if _pride_key in _pride_labels:
                    raise RuntimeError(('duplicate hook label',func_name,_pride_key))
                _pride_labels.add(_pride_key)
                lines.append('PRIDE_PC_%06X_M%dX%d:;' % _pride_key)
                lines.append('{ uint32_t _pride_target=PrideSceneCompiledPreOpcode(cpu,0x%06Xu);' % _pride_pc)
                lines.append('if(_pride_target&0x80000000u) { RecompReturn _r=(RecompReturn)(_pride_target&0x7fffffffu); cpu_trace_event(cpu,0,CPU_TR_NLR_PROPAGATE,(uint8)_r,0); cpu_trace_mark_nlr_exit(BD_EXIT_KIND_SKIP_PROPAGATION); RecompStackPop(); return (RecompReturn)((int)_r-1); }')
                lines.append('if(_pride_target) { switch((_pride_target&0xffffffu)|((cpu->m_flag&1u)<<24)|((cpu->x_flag&1u)<<25)) {')
                lines.append('PRIDE_COMPILED_REDIRECT_CASES')
                lines.append('default: PrideSceneCompiledUnmapped(cpu,0x%06Xu,_pride_target); } } }' % _pride_pc)
'''
    source=source.replace(loop,loop+injection)
    ending='    return "\\n".join(src) + "\\n"'
    assert source.count(ending)==1
    replacement='''    _pride_result = "\\n".join(src) + "\\n"
    if _pride_labels:
        _pride_cases = []
        for _pc,_m,_x in sorted(_pride_labels):
            _pride_cases.append('case 0x%08Xu: goto PRIDE_PC_%06X_M%dX%d;' % (_pc|(_m<<24)|(_x<<25),_pc,_m,_x))
        _pride_result = '#include "pride_scene_compiled_hooks_api.h"\\n' + _pride_result.replace('PRIDE_COMPILED_REDIRECT_CASES','\\n'.join(_pride_cases))
        PRIDE_EMITTED[func_name] = [list(k) for k in sorted(_pride_labels)]
    return _pride_result'''
    source=source.replace(ending,replacement)
    emitted={};emitter.__dict__.update(PRIDE_POINTS=points,PRIDE_EMITTED=emitted)
    exec(compile(source,str(compiler),'exec'),emitter.__dict__)
    args=[str(backend/'tools/v2_emit.py'),'--rom',str(rom_path),'--cfg-dir',str(ROOT/'engine/recomp'),
          '--out-dir',str(out),'--no-host-root-scan','--cfg-roots','--analysis-backend','native',
          '--max-insns','4096','--max-nodes','100000','--bank-shard-threshold-kib','4096','--bank-shard-pc-span','0x800']
    sys.argv=args
    # The emitter's disk cache cannot see the in-memory extension. Invalidate
    # its metadata explicitly so every run observes this wrapper and hook set.
    (out/'.snesrecomp-cache.json').unlink(missing_ok=True)
    try:runpy.run_path(args[0],run_name='__main__')
    except SystemExit as e:
        if e.code not in (None,0):raise
    files=[p for p in out.glob('bank*.c') if 'PrideSceneCompiledPreOpcode' in p.read_text()]
    assert emitted and files,'instrumentation must be freshly emitted'
    # Sharding can detach a per-function include from its first consumer.
    # Declare the bridge before every instruction in each affected unit.
    for path in files:
        path.write_text('#include "pride_scene_compiled_hooks_api.h"\n'+path.read_text())
    original=ROOT/'engine/generated/snesrecomp/program_manifest.json'
    assert json.loads(original.read_text())==json.loads((out/'program_manifest.json').read_text())
    report=dict(result='GENERATED',scope=__doc__,hook_pcs=sorted(points),redirect_pcs=sorted(redirects),
        functions=emitted,instrumented_units=[p.name for p in files],
        compiled_ownership_verified=False,production_modified=False,original_analysis_manifest_exact=True,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in
            [Path(__file__),compiler,rom_path,*hook_sources]},
        generated_sha256={p.name:digest(p) for p in files})
    (out.parent/'generation-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Isolated compiled hook generation: '+str(len(files))+' units, '+str(len(emitted))+' functions',flush=True)


if __name__=='__main__':main()
