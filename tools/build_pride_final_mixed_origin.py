"""Relink the private final-scene host/compositor with selected-origin capture."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    build=ROOT/'build/pride-final-standalone';prior=ROOT/'build/pride-title-fade2'
    bound(prior/'build-report.json')
    out=ROOT/'build/pride-final-mixed-origin';out.mkdir()
    db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=build))
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:]
    for label,suffix,previous in [('host','/final/pride_final_host.c',(prior/'host.obj').as_posix()),
                                 ('wide','/final/pride_final_wide.c',None)]:
        entry=next(r for r in db if r.get('file','').endswith(suffix));cmd=argv(entry['command'])
        obj=out/(label+'.obj')
        for flag,value in [('-o',obj),('-MF',out/(label+'.d')),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
        with (out/(label+'-compile.log')).open('wb') as log:
            subprocess.run(cmd,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        old=previous or entry['output'];assert inputs.count(old)==1
        inputs[inputs.index(old)]=obj.as_posix()
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs));binary=out/'player.exe'
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static',
            '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
            '@'+str(rsp),'-o',str(binary)],cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',
        *sorted((ROOT/'engine/runner/pride/final').glob('*.inc')),
        ROOT/'engine/runner/pride/final/pride_final_host.c',ROOT/'engine/runner/pride/final/pride_final_wide.c']
    result=dict(result='BUILT',binary_sha256=digest(binary),fresh_standalone_graph_claimed=False,
        guest_sources_or_objects_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        link_inputs_sha256={(build/p).resolve().relative_to(ROOT).as_posix():digest(build/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('BUILT',result['binary_sha256'],flush=True)


if __name__=='__main__':main()
