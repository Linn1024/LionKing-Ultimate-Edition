"""Relink52 changing only the checkpoint's user-facing capability description."""
import json
import shutil
import subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    previous_base=ROOT/'build/pride-checkpoint-animation52';previous_path=previous_base/'build-report.json';previous=bound(previous_path)
    out=ROOT/'build/pride-checkpoint-capability53';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    patch=ROOT/'engine/cmake/game-patches/zzz-checkpoint-animation-resource.hunks'
    archive=ROOT/'build/pride-checkpoint-capability53-baseline'/patch.relative_to(ROOT)
    oldline=next(line for line in archive.read_text().splitlines() if 'native repeating' in line or '{"gameplay.levels.pride_lands.checkpoint_animation"' in line)
    newline=next(line for line in patch.read_text().splitlines() if '{"gameplay.levels.pride_lands.checkpoint_animation"' in line)
    oldtext=oldline.split(', "',2)[-1] if False else oldline
    apply=['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),
           '--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')]
    subprocess.run(apply,check=True)
    before=(previous_base/'game/tlk_resources.c').read_text();after=(out/'game/tlk_resources.c').read_text()
    assert before.count(oldline)==1 and after==before.replace(oldline,newline)
    cmd=previous['compiles']['resources'].copy()
    for flag,value in [('-c',out/'game/tlk_resources.c'),('-o',out/'resources.obj'),('-MT',out/'resources.obj'),('-MF',out/'resources.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=argv('link '+(previous_base/'link.rsp').read_text())[1:]
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==previous_base/'resources.obj']
    assert len(indices)==1;inputs[indices[0]]=(out/'resources.obj').as_posix()
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(previous_base/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(previous['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==321 and len(linked)==322
    paths=[Path(__file__),previous_path,patch,archive,rsp,previous_base/'game/tlk_resources.c',out/'game/tlk_resources.c']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles={'resources':cmd},apply=apply,
                link_inputs_sha256=linked,unchanged_prior_inputs=unchanged,description_only_source_delta=True,
                before_line=oldline,after_line=newline,gameplay_or_renderer_logic_modified=False,
                fresh_standalone_graph_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
