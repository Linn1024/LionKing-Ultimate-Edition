"""Relink published72 with independently selected original lizard voice timing."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    parent=ROOT/'build/pride-hyena-voice72';bp=parent/'build-report.json';prior=bound(bp)
    generation=ROOT/'build/pride-lizard-voice74-generation';gp=generation/'generation-report.json';generated=bound(gp)
    oldgp=ROOT/'build/pride-hyena-voice71-generation/generation-report.json';oldg=bound(oldgp)
    assert generated['result']=='GENERATED' and generated['program_contract_sha256']==oldg['program_contract_sha256']
    for unit in oldg['instrumented_units']:assert digest(generation/'hooks'/unit)==digest(oldgp.parent/'hooks'/unit),unit
    out=ROOT/'build/pride-lizard-voice74';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    oldunit=cwd/'game-program/native/bankc1_part1c_v2.c';newunit=generation/'hooks'/oldunit.name
    diff=list(difflib.unified_diff(oldunit.read_text().splitlines(),newunit.read_text().splitlines()))
    (out/'generated-unit.diff').write_text('\n'.join(diff)+'\n')
    assert not any(line.startswith('-') and not line.startswith('---') for line in diff)
    assert newunit.read_text().count('PrideSceneCompiledPreOpcode(cpu,0xC1650Eu)')==1
    commands={};compiles={}
    for label,patches,source,target in [
        ('game',ROOT/'engine/cmake/game-patches',ROOT/'engine',out/'game'),
        ('frontend',ROOT/'engine/cmake/final-frontend-patches',cwd/'native-engine/tlk_pride_final_player_host-frontend/host',out/'frontend')]:
        cmd=[sys.executable,str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(patches),'--snesrecomp',str(source),'--out',str(target)]
        commands[label]=cmd
        with (out/(label+'-patch.log')).open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copy2(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'/name,out/'frontend'/name)
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
    def linked_row(suffix):
        match=[r for r in rows if r.get('output','').replace('\\','/').endswith(suffix) and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in prior['link_inputs_sha256']]
        assert len(match)==1,(suffix,len(match));return match[0]
    lizard=linked_row('/runner/tlk_lizard_audio.c.obj');unit=linked_row('/native/'+oldunit.name+'.obj')
    tasks=[('audio',prior['compiles']['audio'],out/'game/tlk_audio.c',parent/'audio.obj'),
           ('resources',prior['compiles']['resources'],out/'game/tlk_resources.c',parent/'resources.obj'),
           ('host',prior['compiles']['host'],ROOT/'engine/runner/pride/final/pride_final_host.c',parent/'host.obj'),
           ('lizard',argv(lizard['command']),ROOT/'engine/runner/tlk_lizard_audio.c',(cwd/lizard['output']).resolve()),
           ('unit',argv(unit['command']),newunit,(cwd/unit['output']).resolve())]
    inputs=argv('link '+(parent/'link.rsp').read_text())[1:]
    for label,template,source,old in tasks:
        cmd=template.copy()
        for flag,value in [('-c',source),('-o',out/(label+'.obj')),('-MT',out/(label+'.obj')),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        if label in ('audio','resources'):cmd+=['-DTLK_LIZARD_VOICE_TIMING_AVAILABLE=1']
        if label=='unit':cmd+=['-I'+str(ROOT/'engine/runner/pride')]
        if label=='host':
            indices=[i for i,p in enumerate(cmd) if p.startswith('-DTLK_PRIDE_FRONTEND_SOURCE=')];assert len(indices)==1
            cmd[indices[0]]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old)
        inputs[indices[0]]=(out/(label+'.obj')).as_posix();compiles[label]=cmd;print('compiled',label,flush=True)
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copy2(parent/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==317 and len(linked)==322
    paths=[Path(__file__),bp,gp,oldgp,rsp,oldunit,newunit,ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/runner/tlk_audio.h',
           ROOT/'engine/runner/tlk_lizard_audio.c',ROOT/'engine/runner/tlk_lizard_audio.h',ROOT/'engine/runner/tlk_lizard_voice_policy.h',
           ROOT/'engine/runner/tlk_resources.c',ROOT/'engine/recomp/pride_hooks.json',ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',
           ROOT/'engine/cmake/final-frontend-patches/lizard-voice-timing.hunks',out/'game/tlk_audio.c',out/'game/tlk_resources.c',out/'frontend/sdl_main.c']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),commands=commands,compiles=compiles,link_inputs_sha256=linked,
                unchanged_public72_inputs=unchanged,original_game_instructions_or_assets_modified=False,fresh_full_graph_claimed=False,
                compiled_entry='C1650E',published=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
