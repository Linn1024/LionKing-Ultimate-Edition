"""Relink the reviewed final player with independent original attack ordering."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-pickup-flight35';old=bound(prior/'build-report.json')
    flight=bound(ROOT/'build/pride-pickup-flight34/build-report.json')
    nav=bound(ROOT/'build/pride-title-navigation23/build-report.json')
    gen=ROOT/'build/pride-porcupine-hooks';generation=bound(gen/'generation-report.json')
    assert all(digest(gen/p)==sha for p,sha in generation['generated_sha256'].items())
    out=ROOT/'build/pride-porcupine36';out.mkdir();cwd=ROOT/'build/pride-final-standalone'
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/final-frontend-patches'),
                    '--snesrecomp',str(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'),'--out',str(out/'frontend')],check=True)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):
        shutil.copyfile(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'/name,out/'frontend'/name)
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),
                    '--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],check=True)
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:]
    c1=next(p for p in old['link_inputs_sha256'] if p.endswith('native/bankc1_part1b_v2.c.obj'))
    db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=cwd))
    entry=next(r for r in db if r.get('output','').replace('\\','/').endswith('tlk_pride_final_player_native.dir/__/game-program/native/bankc1_part1b_v2.c.obj'))
    tasks=[('host',flight['compiles']['host'].copy(),ROOT/'engine/runner/pride/final/pride_final_host.c',ROOT/'build/pride-pickup-flight34/host.obj'),
           ('resources',flight['compiles']['resources'].copy(),out/'game/tlk_resources.c',ROOT/'build/pride-pickup-flight34/resources.obj'),
           ('backend-state',old['compiles']['backend-state'].copy(),out/'game/tlk_savestate.c',prior/'backend-state.obj'),
           ('attack',nav['compiles']['state'].copy(),ROOT/'engine/runner/tlk_porcupine_attack.c',None),
           ('attack-runtime',nav['compiles']['state'].copy(),ROOT/'engine/runner/tlk_porcupine_attack_runtime.c',None),
           ('c1',argv(entry['command']),gen/'hooks/bankc1_part1b_v2.c',ROOT/c1)]
    compiles={}
    for label,cmd,source,previous in tasks:
        obj=out/(label+'.obj')
        for flag,value in [('-c',source),('-o',obj),('-MF',out/(label+'.d')),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
        if label=='host':
            i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
            cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        if label=='c1':cmd.append('-I'+str(ROOT/'engine/runner/pride'))
        with (out/(label+'-compile.log')).open('wb') as log:
            subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        if previous is None:inputs.append(obj.as_posix())
        else:
            matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==previous.resolve()]
            assert len(matches)==1,(label,matches);inputs[matches[0]]=obj.as_posix()
        compiles[label]=cmd
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static',
                        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',ROOT/'build/pride-pickup-flight34/build-report.json',
           ROOT/'build/pride-title-navigation23/build-report.json',gen/'generation-report.json',
           out/'frontend/sdl_main.c',out/'game/tlk_resources.c',out/'game/tlk_savestate.c',
           ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',*sorted((ROOT/'engine/runner').glob('tlk_porcupine*.[ch]')),
           *sorted((ROOT/'engine/cmake/final-frontend-patches').glob('*.hunks')),
           ROOT/'engine/cmake/game-patches/pride-porcupine-attack-resource.hunks',
           ROOT/'engine/cmake/game-patches/zzz-porcupine-attack-save.hunks']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,
                fresh_standalone_graph_claimed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                link_inputs_sha256={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
