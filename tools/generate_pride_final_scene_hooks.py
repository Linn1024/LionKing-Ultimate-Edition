"""Emit final-life hook extension through the existing patched codegen copy."""
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest

def main():
    out=ROOT/'build/pride-final-compiled-generated2';out.mkdir()
    base=ROOT/'engine/recomp/pride_hooks.json';extra=ROOT/'engine/recomp/pride_final_hooks.json'
    manifest=json.loads(base.read_text());extension=json.loads(extra.read_text())
    points=sorted(set(manifest['hook_pcs'])|set(extension['hook_pcs']))
    backend=ROOT/'build/pride-bounce-owner-work/game-program/codegen'
    compiler=backend/'recompiler/v2/emit_function.py';assert 'TLK_COMPILED_HOOK_POINTS' in compiler.read_text()
    rom=ROOT/'Lion King, The (USA).sfc';assert digest(rom)==manifest['rom_sha256']
    target=out/'hooks';env={k:v for k,v in os.environ.items() if k!='TLK_COMPILED_HOOK_POINTS'}
    env['TLK_COMPILED_HOOK_POINTS']=json.dumps(points)
    command=[sys.executable,str(backend/'tools/v2_emit.py'),'--rom',str(rom),'--cfg-dir',str(ROOT/'engine/recomp'),
        '--out-dir',str(target),'--no-host-root-scan','--cfg-roots','--analysis-backend','native',
        '--max-insns','4096','--max-nodes','100000','--bank-shard-threshold-kib','4096','--bank-shard-pc-span','0x800']
    with (out/'generate.log').open('wb') as log:
        subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
    files=[p for p in sorted(target.glob('bank*.c')) if 'PrideSceneCompiledPreOpcode' in p.read_text()]
    for p in files:p.write_text('#include "pride_scene_compiled_hooks_api.h"\n'+p.read_text())
    originals=ROOT/'build/pride-bounce-owner-work/game-program/native'
    changed=[p for p in files if digest(p)!=digest(originals/p.name)]
    found={point:[] for point in extension['hook_pcs']}
    for p in files:
        text=p.read_text().lower()
        for point in found:
            if 'pride_pc_'+point[2:]+'_' in text:found[point].append(p.name)
    assert all(found.values()),found
    checks=dict(program_manifest_unchanged=json.loads((target/'program_manifest.json').read_text())==
        json.loads((originals/'program_manifest.json').read_text()),all_final_hooks_emitted=all(found.values()))
    paths=[Path(__file__),base,extra,compiler,rom]
    result=dict(result='GENERATED' if all(checks.values()) else 'FAIL',checks=checks,command=command,
        hook_pcs=points,final_sites=found,instrumented_units=[p.name for p in files],changed_units=[p.name for p in changed],
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        generated_sha256={p.name:digest(p) for p in files})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(files),'hook units;',len(changed),'changed units',flush=True);assert all(checks.values())

if __name__=='__main__':main()
