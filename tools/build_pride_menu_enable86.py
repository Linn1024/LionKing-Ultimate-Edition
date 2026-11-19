"""Replace one output-only ownership object; keep accepted menu voices filtered."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    parent=ROOT/'build/pride-menu-output83';bp=parent/'build-report.json';prior=bound(bp)
    component=ROOT/'build/pride-menu-enable86-owner-component/report.json';assert bound(component)['result']=='PASS'
    out=ROOT/'build/pride-menu-enable86';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    source=ROOT/'engine/runner/tlk_native_audio_owner.c';cmd=prior['compiles']['owner'].copy()
    for flag,value in [('-c',source),('-o',out/'owner.obj'),('-MT',out/'owner.obj'),('-MF',out/'owner.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    inputs=argv('link '+(parent/'link.rsp').read_text())[1:]
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==parent/'owner.obj'];assert len(indices)==1
    inputs[indices[0]]=(out/'owner.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copy2(parent/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    assert len(linked)==322 and sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==321
    compiles=dict(prior['compiles']);compiles['owner']=cmd
    paths=[Path(__file__),bp,component,source,rsp]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,
                unchanged_candidate83_inputs=321,current_owner_schema=3,guest_code_or_audio_queue_modified=False,
                fresh_full_graph_claimed=False,published=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
