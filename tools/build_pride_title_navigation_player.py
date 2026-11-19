"""Build independently selected title navigation, codec, catalog and fresh hooks."""
import json
from pathlib import Path
import shutil
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-title-ready18';previous=bound(prior/'build-report.json')
    resources_build=bound(ROOT/'build/pride-final-resource2/build-report.json')
    gen=ROOT/'build/pride-title-navigation-hooks';generated=bound(gen/'generation-report.json')
    assert all(digest(gen/p)==sha for p,sha in generated['generated_sha256'].items())
    oldgen=ROOT/'build/pride-title-ready-hooks';bound(oldgen/'generation-report.json')
    changed=[p.name for p in sorted((gen/'hooks').glob('bank*.c')) if digest(p)!=digest(oldgen/'hooks'/p.name)]
    assert changed==['bankc4_part1c_v2.c'],changed
    out=ROOT/'build/pride-title-navigation23';out.mkdir()
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),
                    '--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],check=True)
    build=ROOT/'build/pride-final-standalone'
    original=build/'native-engine/tlk_pride_final_player_host-frontend/host'
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/final-frontend-patches'),
                    '--snesrecomp',str(original),'--out',str(out/'frontend')],check=True)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copyfile(original/name,out/'frontend'/name)
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:]
    db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=build))
    tasks=[('host',previous['compiles']['host'].copy(),ROOT/'engine/runner/pride/final/pride_final_host.c',prior/'host.obj'),
           ('state',previous['compiles']['state'].copy(),ROOT/'engine/runner/tlk_final_scene_state.c',prior/'state.obj'),
           ('resources',resources_build['compiles']['resources'].copy(),out/'game/tlk_resources.c',ROOT/'build/pride-final-resource2/resources.obj'),
           ('navigation',previous['compiles']['state'].copy(),ROOT/'engine/runner/tlk_title_navigation.c',None)]
    for name in changed:
        entry=next(r for r in db if r.get('file','').endswith('/'+name) and any(v in r['output'] for v in ('/tlk_pride_final_player_guest.dir/','/tlk_pride_final_player_native.dir/')))
        old=prior/(name+'.obj')
        tasks.append((name,previous['compiles'][name].copy(),gen/'hooks'/name,old))
    compiles={}
    for label,cmd,source,old in tasks:
        obj=out/(label+'.obj')
        for flag,value in [('-c',source),('-o',obj),('-MF',out/(label+'.d')),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
        if label=='host':
            i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
            cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        if old is None:inputs.append(obj.as_posix())
        else:
            matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (build/p).resolve()==old.resolve()]
            assert len(matches)==1,(label,matches);inputs[matches[0]]=obj.as_posix()
        compiles[label]=cmd
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static',
        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine','@'+str(rsp),'-o',str(out/'player.exe')],
        cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',gen/'generation-report.json',oldgen/'generation-report.json',
           ROOT/'engine/runner/tlk_final_scene_state.c',ROOT/'engine/runner/tlk_final_scene_state.h',ROOT/'engine/recomp/pride_final_hooks.json',
           ROOT/'engine/runner/tlk_title_navigation.c',ROOT/'engine/runner/tlk_title_navigation.h',ROOT/'engine/runner/tlk_resources.c',
           ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',
           out/'game/tlk_resources.c',ROOT/'engine/cmake/game-patches/pride-title-navigation-resource.hunks',
           out/'frontend/sdl_main.c',ROOT/'engine/cmake/final-frontend-patches/title-navigation.hunks',
           ROOT/'engine/runner/pride/pride_present.inc',
           ROOT/'engine/runner/pride/final/pride_final_host.c',*sorted((ROOT/'engine/runner/pride/final').glob('*.inc'))]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,changed_guest_units=changed,
                fresh_standalone_graph_claimed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                link_inputs_sha256={(build/p).resolve().relative_to(ROOT).as_posix():digest(build/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
