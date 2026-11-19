"""Relink maintained installed title upload and its newly generated compiled hook."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='build/pride-title-upload16');parser.add_argument('--generation',default='build/pride-title-upload-hooks3');args=parser.parse_args()
    build=ROOT/'build/pride-final-standalone';prior=ROOT/'build/pride-title-native15';bound(prior/'build-report.json')
    generation=ROOT/args.generation;generated=bound(generation/'generation-report.json')
    assert all(digest(generation/p)==sha for p,sha in generated['generated_sha256'].items())
    previous=ROOT/'build/pride-title-fade-hooks';bound(previous/'generation-report.json')
    changed=[p.name for p in sorted((generation/'hooks').glob('bank*.c')) if digest(p)!=digest(previous/'hooks'/p.name)]
    assert changed==['bankc2_part13_v2.c','bankc2_part14_v2.c'],changed
    out=ROOT/args.output;out.mkdir();frontend=out/'frontend'
    original=build/'native-engine/tlk_pride_final_player_host-frontend/host'
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/final-frontend-patches'),
                    '--snesrecomp',str(original),'--out',str(frontend)],check=True)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copyfile(original/name,frontend/name)
    prior_build=json.loads((prior/'build-report.json').read_text())
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:]
    db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=build))
    compiles={}
    tasks=[('host',prior_build['compiles']['host'].copy(),ROOT/'engine/runner/pride/final/pride_final_host.c',prior/'host.obj'),
           ('title',prior_build['compiles']['host'].copy(),ROOT/'engine/runner/tlk_title_bank.c',None)]
    for name in changed:
        guest=next(r for r in db if r.get('file','').endswith('/'+name) and '/tlk_pride_final_player_guest.dir/' in r['output'])
        tasks.append((name,argv(guest['command']),generation/'hooks'/name,build/guest['output']))
    for label,cmd,source,old in tasks:
        obj=out/(label+'.obj')
        for flag,value in [('-c',source),('-o',obj),('-MF',out/(label+'.d')),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
        if label=='host':
            i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(frontend/'sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        if label=='title':inputs.append(obj.as_posix())
        else:
            matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (build/p).resolve()==old.resolve()]
            assert len(matches)==1,(label,matches);inputs[matches[0]]=obj.as_posix()
        compiles[label]=cmd
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static',
        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine','@'+str(rsp),'-o',str(out/'player.exe')],cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',generation/'generation-report.json',previous/'generation-report.json',frontend/'sdl_main.c',
        ROOT/'engine/cmake/final-frontend-patches/presentation.hunks',ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',ROOT/'engine/recomp/pride_final_hooks.json',
        ROOT/'engine/runner/pride/final/pride_final_host.c',ROOT/'engine/runner/tlk_title_bank.c',ROOT/'engine/runner/tlk_title_bank.h',
        *sorted((ROOT/'engine/runner/pride/final').glob('*.inc'))]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),changed_guest_units=changed,compiles=compiles,
        fresh_standalone_graph_claimed=False,framework_or_config_contract_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        link_inputs_sha256={(build/p).resolve().relative_to(ROOT).as_posix():digest(build/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)

if __name__=='__main__':main()
