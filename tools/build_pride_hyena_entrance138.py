"""Integrate independently selected entrance geometry; retain all other guest units."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

def main():
    parent=ROOT/'build/pride-resource-tree118';bp=parent/'build-report.json';prior=bound(bp)
    assert bound(parent/'bindings/report.json')['result']=='PASS'
    proofs=[ROOT/'build'/name/'report.json' for name in ('pride-hyena-entrance132','pride-hyena-countdown133')]
    for p in proofs:assert bound(p)['result']=='PASS'
    generation=ROOT/'build/pride-hyena-entrance138-generation';gp=generation/'generation-report.json';g=bound(gp)
    oldgp=ROOT/'build/pride-lizard-voice74-generation/generation-report.json';old=bound(oldgp)
    assert g['program_contract_sha256']==old['program_contract_sha256']
    for unit in old['instrumented_units']:assert digest(generation/'hooks'/unit)==digest(oldgp.parent/'hooks'/unit),unit
    assert digest(generation/'rng/bankc0_part1f_v2.c')==digest(oldgp.parent/'rng/bankc0_part1f_v2.c')
    subprocess.run(['python',str(ROOT/'engine/scripts/validate_pride_generation.py'),'--generation',str(generation),'--rom',str(ROOT/'Lion King, The (USA).sfc')],check=True)
    out=ROOT/'build/pride-hyena-entrance139';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    oldunit=cwd/'game-program/native/bankc0_part17_v2.c';newunit=generation/'hooks'/oldunit.name
    diff=list(difflib.unified_diff(oldunit.read_text().splitlines(),newunit.read_text().splitlines()))
    (out/'generated-unit.diff').write_text('\n'.join(diff)+'\n')
    assert not any(line.startswith('-') and not line.startswith('---') for line in diff)
    assert newunit.read_text().count('PrideSceneCompiledPreOpcode(cpu,0xC03BDBu)')==1
    commands={};compiles=dict(prior['compiles'])
    for label,patches,source,target in [('game',ROOT/'engine/cmake/game-patches',ROOT/'engine',out/'game'),
        ('frontend',ROOT/'engine/cmake/final-frontend-patches',cwd/'native-engine/tlk_pride_final_player_host-frontend/host',out/'frontend')]:
        cmd=['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(patches),'--snesrecomp',str(source),'--out',str(target)];commands[label]=cmd
        with (out/(label+'-patch.log')).open('wb') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copy2(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'/name,out/'frontend'/name)
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
    match=[r for r in rows if r.get('output','').replace('\\','/').endswith('/native/'+oldunit.name+'.obj') and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in prior['link_inputs_sha256']]
    assert len(match)==1
    unit=match[0];unit_cmd=argv(unit['command']);inputs=argv('link '+(parent/'link.rsp').read_text())[1:]
    for label,template,source in [('resources',prior['compiles']['resources'],out/'game/tlk_resources.c'),
        ('host',prior['compiles']['host'],ROOT/'engine/runner/pride/final/pride_final_host.c'),
        ('entrance',prior['compiles']['probe'],ROOT/'engine/runner/tlk_hyena_entrance.c'),('unit',unit_cmd,newunit)]:
        cmd=template.copy();previous=(cwd/Path(cmd[cmd.index('-o')+1])).resolve();obj=out/(label+'.obj')
        for flag,value in [('-c',source),('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        if label=='resources':cmd+=['-DTLK_HYENA_ENTRANCE_AVAILABLE=1']
        if label=='unit':cmd+=['-I'+str(ROOT/'engine/runner/pride')]
        if label=='host':
            i=next(i for i,p in enumerate(cmd) if p.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=300)
        if label=='entrance':inputs.insert(0,obj.as_posix())
        else:
            indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==previous];assert len(indices)==1,(label,previous)
            inputs[indices[0]]=obj.as_posix()
        compiles[label]=cmd;print('compiled',label,flush=True)
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copy2(parent/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert len(linked)==324 and unchanged==320
    assert digest(parent/'player.exe')==prior['binary_sha256']
    paths=[Path(__file__),bp,parent/'bindings/report.json',gp,oldgp,*proofs,rsp,oldunit,newunit,out/'frontend/sdl_main.c',out/'game/tlk_resources.c',
        ROOT/'engine/runner/tlk_hyena_entrance.c',ROOT/'engine/runner/tlk_hyena_entrance.h',ROOT/'engine/runner/tlk_hyena_entrance_policy.h',
        ROOT/'engine/runner/tlk_resources.c',ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',ROOT/'engine/cmake/final-frontend-patches/hyena-entrance-window.hunks']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),commands=commands,compiles=compiles,link_inputs_sha256=linked,
        unchanged_public118_inputs=unchanged,original_game_instruction_changes=False,generated_change='One emitted pre-opcode hook C03BDB; add-only source diff retained.',
        published=False,fresh_full_graph_claimed=False,current_build_saves_only=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)
if __name__=='__main__':main()
