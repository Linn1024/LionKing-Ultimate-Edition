"""Add verified independent walking probe without altering original game objects."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    parent=ROOT/'build/pride-menu-enable86';bp=parent/'build-report.json';prior=bound(bp)
    proof=ROOT/'build/pride-hyena-probe98/report.json';assert bound(proof)['result']=='PASS'
    component=ROOT/'build/pride-hyena-probe97-component';test=component/'test.exe'
    result=subprocess.run([str(test)],capture_output=True,text=True,check=True);assert result.stdout.strip()=='PASS 4296 checks'
    component_paths=[ROOT/'engine/tests/hyena_walking_probe_test.c',ROOT/'engine/runner/tlk_hyena_probe.c',ROOT/'engine/runner/tlk_hyena_probe.h',test]
    (component/'report.json').write_text(json.dumps(dict(result='PASS',checks=dict(scope_cpu_and_ram_guards4296=True),output=result.stdout,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in component_paths}),indent=2)+'\n')
    out=ROOT/'build/pride-hyena-probe97';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    generation=ROOT/'build/pride-lizard-voice74-generation/generation-report.json';g=bound(generation)
    assert digest(ROOT/'engine/recomp/pride_hooks.json')==g['source_sha256']['engine/recomp/pride_hooks.json']
    commands={};compiles=dict(prior['compiles'])
    for label,patches,source,target in [
        ('game',ROOT/'engine/cmake/game-patches',ROOT/'engine',out/'game'),
        ('frontend',ROOT/'engine/cmake/final-frontend-patches',cwd/'native-engine/tlk_pride_final_player_host-frontend/host',out/'frontend')]:
        cmd=['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(patches),'--snesrecomp',str(source),'--out',str(target)];commands[label]=cmd
        with (out/(label+'-patch.log')).open('wb') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copy2(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'/name,out/'frontend'/name)
    inputs=argv('link '+(parent/'link.rsp').read_text())[1:]
    for label,source in [('resources',out/'game/tlk_resources.c'),('host',ROOT/'engine/runner/pride/final/pride_final_host.c'),('probe',ROOT/'engine/runner/tlk_hyena_probe.c')]:
        cmd=prior['compiles']['owner' if label=='probe' else label].copy();old=Path(cmd[cmd.index('-o')+1])
        for flag,value in [('-c',source),('-o',out/(label+'.obj')),('-MT',out/(label+'.obj')),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        if label=='resources':cmd+=['-DTLK_HYENA_PROBE_AVAILABLE=1']
        if label=='host':
            indices=[i for i,p in enumerate(cmd) if p.startswith('-DTLK_PRIDE_FRONTEND_SOURCE=')];assert len(indices)==1
            cmd[indices[0]]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        if label=='probe':inputs.insert(0,(out/(label+'.obj')).as_posix())
        else:
            indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old)
            inputs[indices[0]]=(out/(label+'.obj')).as_posix()
        compiles[label]=cmd;print('compiled',label,flush=True)
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copy2(parent/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==320 and len(linked)==323
    paths=[Path(__file__),bp,proof,component/'report.json',generation,rsp,ROOT/'engine/runner/tlk_resources.c',ROOT/'engine/runner/tlk_hyena_probe.c',ROOT/'engine/runner/tlk_hyena_probe.h',
           ROOT/'engine/runner/tlk_hyena_probe_policy.h',ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',ROOT/'engine/cmake/final-frontend-patches/hyena-walking-probe.hunks',out/'frontend/sdl_main.c',out/'game/tlk_resources.c']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),commands=commands,compiles=compiles,link_inputs_sha256=linked,unchanged_public86_inputs=unchanged,
                original_game_objects_or_assets_modified=False,fresh_full_graph_claimed=False,published=False,current_build_saves_only=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
