"""Build entry-once MD hyena voice from maintained regenerated hooks and sources."""
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
    parent=ROOT/'build/pride-music-output65';bp=parent/'build-report.json';prior=bound(bp)
    generation=ROOT/'build/pride-hyena-voice71-generation';gp=generation/'generation-report.json';generated=bound(gp)
    assert generated['result']=='GENERATED'
    out=ROOT/'build/pride-hyena-voice72';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    old_unit=cwd/'game-program/native/bankc1_part18_v2.c';new_unit=generation/'hooks'/old_unit.name
    diff=list(difflib.unified_diff(old_unit.read_text().splitlines(),new_unit.read_text().splitlines()))
    (out/'generated-unit.diff').write_text('\n'.join(diff)+'\n')
    assert new_unit.read_text().count('PrideSceneCompiledPreOpcode(cpu,0xC14535u)')==1
    # This bank previously had no compiled hooks. The generator adds only its
    # API includes and one reviewed entry hook; all original bodies stay intact.
    removed=[x for x in diff if x.startswith('-') and not x.startswith('---')]
    assert not removed
    commands={};compiles={}
    for label,patches,source,target in [
        ('game',ROOT/'engine/cmake/game-patches',ROOT/'engine',out/'game'),
        ('frontend',ROOT/'engine/cmake/final-frontend-patches',cwd/'native-engine/tlk_pride_final_player_host-frontend/host',out/'frontend')]:
        cmd=[sys.executable,str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(patches),'--snesrecomp',str(source),'--out',str(target)]
        commands[label]=cmd
        with (out/(label+'-patch.log')).open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):
        shutil.copy2(cwd/'native-engine/tlk_pride_final_player_host-frontend/host'/name,out/'frontend'/name)
    hostbp=ROOT/'build/pride-checkpoint-animation52/build-report.json';host=bound(hostbp)
    resourcebp=ROOT/'build/pride-checkpoint-capability53/build-report.json';resources=bound(resourcebp)
    audiobp=ROOT/'build/pride-music-output62/build-report.json';audio=bound(audiobp)
    inputs=argv('link '+(parent/'link.rsp').read_text())[1:]
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
    def linked_row(suffix):
        match=[r for r in rows if r.get('output','').replace('\\','/').endswith(suffix) and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in prior['link_inputs_sha256']]
        assert len(match)==1,(suffix,len(match));return match[0]
    hyena=linked_row('/runner/tlk_hyena_audio.c.obj');unit=linked_row('/native/'+old_unit.name+'.obj')
    tasks=[('audio',audio['compiles']['audio'],out/'game/tlk_audio.c',ROOT/'build/pride-music-output62/audio.obj'),
           ('resources',resources['compiles']['resources'],out/'game/tlk_resources.c',ROOT/'build/pride-checkpoint-capability53/resources.obj'),
           ('host',host['compiles']['host'],ROOT/'engine/runner/pride/final/pride_final_host.c',ROOT/'build/pride-checkpoint-animation52/host.obj'),
           ('hyena',argv(hyena['command']),ROOT/'engine/runner/tlk_hyena_audio.c',(cwd/hyena['output']).resolve()),
           ('unit',argv(unit['command']),new_unit,(cwd/unit['output']).resolve())]
    for label,template,source,old in tasks:
        cmd=template.copy()
        for flag,value in [('-c',source),('-o',out/(label+'.obj')),('-MT',out/(label+'.obj')),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        if label in ('audio','resources'):cmd+=['-DTLK_HYENA_VOICE_ENTRY_AVAILABLE=1']
        if label=='unit':cmd+=['-I'+str(ROOT/'engine/runner/pride')]
        if label=='host':
            indices=[i for i,p in enumerate(cmd) if p.startswith('-DTLK_PRIDE_FRONTEND_SOURCE=')];assert len(indices)==1
            cmd[indices[0]]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old)
        inputs[indices[0]]=(out/(label+'.obj')).as_posix();compiles[label]=cmd
        print('compiled',label,flush=True)
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copy2(parent/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==317 and len(linked)==322
    paths=[Path(__file__),bp,gp,hostbp,resourcebp,audiobp,rsp,old_unit,new_unit,
           ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/runner/tlk_audio.h',ROOT/'engine/runner/tlk_hyena_audio.c',ROOT/'engine/runner/tlk_hyena_audio.h',
           ROOT/'engine/runner/tlk_resources.c',ROOT/'engine/recomp/pride_hooks.json',ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',
           ROOT/'engine/runner/tlk_hyena_voice_policy.h',
           ROOT/'engine/cmake/final-frontend-patches/hyena-voice-entry.hunks',out/'game/tlk_audio.c',out/'game/tlk_resources.c',out/'frontend/sdl_main.c']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),commands=commands,compiles=compiles,link_inputs_sha256=linked,
                unchanged_public65_inputs=unchanged,original_game_instructions_or_assets_modified=False,
                fresh_full_graph_claimed=False,compiled_entry='C14535',published=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
