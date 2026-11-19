"""Relink candidate46 with append-compatible live-graphics save identity."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-sprite-fresh44'
    candidate=ROOT/'build/pride-continue-token46'
    old_path=prior/'build-report.json';old=bound(old_path)
    candidate_path=candidate/'build-report.json';previous=bound(candidate_path)
    out=ROOT/'build/pride-continue-token47';out.mkdir()
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=prior))
    row=next(r for r in rows if r.get('file','').endswith('/pride_final_host.c') and r.get('command'))
    cmd=argv(row['command']);obj=out/'host.obj'
    for flag,value in [('-o',obj),('-MT',obj),('-MF',out/'host.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'host-compile.log').open('wb') as log:
        subprocess.run(cmd,cwd=prior,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    inputs=argv('link '+(candidate/'link.rsp').read_text())[1:]
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (prior/p).resolve()==(prior/row['output']).resolve()]
    assert len(indices)==1;inputs[indices[0]]=obj.as_posix()
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=prior,
                       stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(prior/name,out/name)
    linked={(prior/p).resolve().relative_to(ROOT).as_posix():digest(prior/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    assert len(linked)==322
    assert sum(previous['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==321
    unchanged=sum(old['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==318
    paths=[Path(__file__),old_path,candidate_path,rsp,ROOT/'engine/runner/pride/final/pride_final_host.c',
           ROOT/'engine/runner/pride/pride_practice_probe.c']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles={'host':cmd},
                link_inputs_sha256=linked,unchanged_prior_inputs=unchanged,unchanged_candidate46_inputs=321,
                fresh_standalone_graph_claimed=False,installed_sprite_policy_changed=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
