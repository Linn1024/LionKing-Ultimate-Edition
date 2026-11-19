"""Build maintained title readiness with a fresh generated resume target."""
import json
from pathlib import Path
import shutil
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-title-upload16';previous=bound(prior/'build-report.json')
    state_build=bound(ROOT/'build/pride-title-native15/build-report.json')
    gen=ROOT/'build/pride-title-ready-hooks';generated=bound(gen/'generation-report.json')
    assert all(digest(gen/p)==sha for p,sha in generated['generated_sha256'].items())
    oldgen=ROOT/'build/pride-title-upload-hooks3';bound(oldgen/'generation-report.json')
    changed=[p.name for p in sorted((gen/'hooks').glob('bank*.c')) if digest(p)!=digest(oldgen/'hooks'/p.name)]
    assert changed==['bankc4_part1c_v2.c'],changed
    out=ROOT/'build/pride-title-ready18';out.mkdir()
    shutil.copytree(prior/'frontend',out/'frontend')
    build=ROOT/'build/pride-final-standalone'
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:]
    db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=build))
    tasks=[('host',previous['compiles']['host'].copy(),ROOT/'engine/runner/pride/final/pride_final_host.c',prior/'host.obj'),
           ('state',state_build['compiles']['state'].copy(),ROOT/'engine/runner/tlk_final_scene_state.c',ROOT/'build/pride-title-native15/state.obj')]
    for name in changed:
        entry=next(r for r in db if r.get('file','').endswith('/'+name) and any(v in r['output'] for v in ('/tlk_pride_final_player_guest.dir/','/tlk_pride_final_player_native.dir/')))
        old=next(ROOT/p for p in previous['link_inputs_sha256'] if p.endswith('/'+name+'.obj'))
        tasks.append((name,argv(entry['command'])+['-I'+str(ROOT/'engine/runner/pride')],gen/'hooks'/name,old))
    compiles={}
    for label,cmd,source,old in tasks:
        obj=out/(label+'.obj')
        for flag,value in [('-c',source),('-o',obj),('-MF',out/(label+'.d')),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
        if label=='host':
            i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
            cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (build/p).resolve()==old.resolve()]
        assert len(matches)==1,(label,matches);inputs[matches[0]]=obj.as_posix();compiles[label]=cmd
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static',
        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine','@'+str(rsp),'-o',str(out/'player.exe')],
        cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',gen/'generation-report.json',oldgen/'generation-report.json',
           ROOT/'engine/runner/tlk_final_scene_state.c',ROOT/'engine/runner/tlk_final_scene_state.h',ROOT/'engine/recomp/pride_final_hooks.json',
           ROOT/'engine/runner/pride/final/pride_final_host.c',*sorted((ROOT/'engine/runner/pride/final').glob('*.inc'))]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,changed_guest_units=changed,
                fresh_standalone_graph_claimed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                link_inputs_sha256={(build/p).resolve().relative_to(ROOT).as_posix():digest(build/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
