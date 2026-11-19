"""Build the independent flight adapter and newly instrumented C5 action shard."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='build/pride-pickup-flight31');args=ap.parse_args()
    prior=ROOT/'build/pride-audio-prime30';previous=bound(prior/'build-report.json')
    nav=bound(ROOT/'build/pride-title-navigation23/build-report.json')
    wide=bound(ROOT/'build/pride-title-native15/build-report.json')
    gen=ROOT/'build/pride-pickup-flight-hooks';generation=bound(gen/'generation-report.json')
    assert all(digest(gen/p)==sha for p,sha in generation['generated_sha256'].items())
    out=ROOT/args.output;out.mkdir();cwd=ROOT/'build/pride-final-standalone'
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/final-frontend-patches'),
                    '--snesrecomp',str(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'),'--out',str(out/'frontend')],check=True)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):
        shutil.copyfile(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'/name,out/'frontend'/name)
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),
                    '--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],check=True)
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:]
    old_inputs=previous['link_inputs_sha256']
    c5=next(p for p in old_inputs if p.endswith('native/bankc5_part1a_v2.c.obj'))
    db=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=cwd))
    entry=next(r for r in db if r.get('output','').replace('\\','/').endswith('tlk_pride_final_player_native.dir/__/game-program/native/bankc5_part1a_v2.c.obj'))
    tasks=[('host',previous['compiles']['host'].copy(),ROOT/'engine/runner/pride/final/pride_final_host.c',prior/'host.obj'),
           ('wide',wide['compiles']['wide'].copy(),ROOT/'engine/runner/pride/final/pride_final_wide.c',ROOT/'build/pride-title-native15/wide.obj'),
           ('resources',nav['compiles']['resources'].copy(),out/'game/tlk_resources.c',ROOT/'build/pride-title-navigation23/resources.obj'),
           ('motion',nav['compiles']['state'].copy(),ROOT/'engine/runner/tlk_pickup_flight_motion.c',None),
           ('flight',nav['compiles']['state'].copy(),ROOT/'engine/runner/tlk_pickup_flight_runtime.c',None),
           ('c5',argv(entry['command']),gen/'hooks/bankc5_part1a_v2.c',ROOT/c5)]
    compiles={}
    for label,cmd,source,old in tasks:
        obj=out/(label+'.obj')
        for flag,value in [('-c',source),('-o',obj),('-MF',out/(label+'.d')),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
        if label=='host':
            i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
            cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        if label=='wide':cmd.append('-DTLK_PRIDE_FINAL_AVAILABLE=1')
        if label=='c5':cmd.append('-I'+str(ROOT/'engine/runner/pride'))
        with (out/(label+'-compile.log')).open('wb') as log:
            subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        if old is None:inputs.append(obj.as_posix())
        else:
            matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old.resolve()]
            assert len(matches)==1,(label,matches);inputs[matches[0]]=obj.as_posix()
        compiles[label]=cmd
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static','-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
                        '@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',ROOT/'build/pride-title-navigation23/build-report.json',
           ROOT/'build/pride-title-native15/build-report.json',gen/'generation-report.json',out/'frontend/sdl_main.c',out/'game/tlk_resources.c',
           ROOT/'engine/runner/tlk_wide.c',ROOT/'engine/runner/tlk_wide.h',ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',
           *sorted((ROOT/'engine/runner').glob('tlk_pickup_flight*.[ch]')),
           *sorted((ROOT/'engine/cmake/final-frontend-patches').glob('*.hunks')),
           ROOT/'engine/cmake/game-patches/pride-pickup-flight-resource.hunks']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,
                fresh_standalone_graph_claimed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                link_inputs_sha256={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
