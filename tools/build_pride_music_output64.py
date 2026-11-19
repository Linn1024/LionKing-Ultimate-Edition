"""Replace only candidate62 music-owner hardware-lifetime handling."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    parent=ROOT/'build/pride-music-output62';bp=parent/'build-report.json';prior=bound(bp)
    out=ROOT/'build/pride-music-output65';out.mkdir(exist_ok=True);assert not (out/'player.exe').exists()
    cwd=ROOT/'build/pride-sprite-fresh44';cmd=prior['compiles']['owner'].copy()
    for flag,value in [('-o',out/'owner.obj'),('-MT',out/'owner.obj'),('-MF',out/'owner.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=argv('link '+(parent/'link.rsp').read_text())[1:]
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==parent/'owner.obj']
    assert len(indices)==1;inputs[indices[0]]=(out/'owner.obj').as_posix()
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(parent/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==321 and len(linked)==322
    paths=[Path(__file__),bp,rsp,ROOT/'engine/runner/tlk_native_audio_owner.c',ROOT/'engine/runner/tlk_native_audio_owner.h']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles={'owner':cmd},link_inputs_sha256=linked,
                unchanged_candidate62_inputs=unchanged,fresh_standalone_graph_claimed=False,
                guest_code_or_native_timing_modified=False,current_owner_schema=2,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
