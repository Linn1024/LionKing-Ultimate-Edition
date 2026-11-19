"""Relink47 with a reviewed shared-parser duration boundary and Sun PCM cue."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-sprite-fresh44';previous_base=ROOT/'build/pride-continue-token47'
    previous_path=previous_base/'build-report.json';previous=bound(previous_path)
    generation=ROOT/'build/pride-continue-token-hooks48';generation_path=generation/'generation-report.json';generated=bound(generation_path)
    assert generated['result']=='GENERATED'
    unit='bankc0_part05_v2.c'
    for name in generated['instrumented_units']:
        if name!=unit:assert digest(generation/'hooks'/name)==digest(prior/'game-program/hooks'/name),name
    out=ROOT/'build/pride-continue-token-behavior50';out.mkdir();commands={};compiles={}
    for label,patches,source,target in [
        ('game','engine/cmake/game-patches',ROOT/'engine',out/'game'),
        ('frontend','engine/cmake/final-frontend-patches',prior/'native-engine/tlk_pride_final_player_host-frontend/host',out/'frontend')]:
        cmd=['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/patches),'--snesrecomp',str(source),'--out',str(target)]
        commands[label]=cmd;subprocess.run(cmd,check=True)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):
        shutil.copyfile(prior/'native-engine/tlk_pride_final_player_host-frontend/host'/name,out/'frontend'/name)
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=prior))
    inputs=argv('link '+(previous_base/'link.rsp').read_text())[1:]
    specifications=[
        ('host','/pride_final_host.c',ROOT/'engine/runner/pride/final/pride_final_host.c',previous_base/'host.obj'),
        ('resources','/game/tlk_resources.c.obj',out/'game/tlk_resources.c',ROOT/'build/pride-continue-token46/resources.obj'),
        ('audio','/game/tlk_audio.c.obj',out/'game/tlk_audio.c',None),
        ('savestate','/game/tlk_savestate.c.obj',out/'game/tlk_savestate.c',None),
        ('animation', '/hooks/'+unit+'.obj',generation/'hooks'/unit,None)]
    for label,suffix,source,old_object in specifications:
        if label=='host':matches=[r for r in rows if r.get('file','').endswith(suffix) and r.get('command')]
        else:matches=[r for r in rows if r.get('output','').replace('\\','/').endswith(suffix) and 'tlk_pride_final_player_' in r.get('output','')]
        assert len(matches)==1,(label,len(matches));row=matches[0];cmd=argv(row['command']);obj=out/(label+'.obj')
        for flag,value in [('-c',source),('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        if label=='host':
            indices=[i for i,p in enumerate(cmd) if p.startswith('-DTLK_PRIDE_FRONTEND_SOURCE=')];assert len(indices)==1
            cmd[indices[0]]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as log:
            subprocess.run(cmd,cwd=prior,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        old_object=old_object or (prior/row['output']).resolve()
        indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (prior/p).resolve()==old_object]
        assert len(indices)==1,(label,old_object);inputs[indices[0]]=obj.as_posix();compiles[label]=cmd
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=prior,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(previous_base/name,out/name)
    linked={(prior/p).resolve().relative_to(ROOT).as_posix():digest(prior/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(previous['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==317 and len(linked)==322
    paths=[Path(__file__),previous_path,generation_path,rsp,ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/runner/pride/pride_practice_probe.c',ROOT/'engine/runner/pride/final/pride_final_host.c',
           ROOT/'engine/runner/tlk_continue_token_timing.h',ROOT/'engine/cmake/game-patches/z-continue-token-resource.hunks',
           ROOT/'engine/cmake/game-patches/zz-continue-token-behavior-resource.hunks',ROOT/'engine/cmake/game-patches/zzzz-continue-token-animation-save.hunks',out/'game/tlk_savestate.c',ROOT/'engine/cmake/final-frontend-patches/continue-token-timing.hunks',
           out/'game/tlk_audio.c',out/'game/tlk_resources.c',out/'frontend/sdl_main.c',generation/'hooks'/unit]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),commands=commands,compiles=compiles,
                link_inputs_sha256=linked,unchanged_prior_inputs=unchanged,fresh_standalone_graph_claimed=False,
                guest_code_bytes_or_data_assets_modified=False,additional_compiled_boundary='C0AD54',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
