"""Build the opening-jump MD battle cue without changing guest instructions."""
import difflib
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound

def main():
    parent=ROOT/'build/pride-native-hud307-installed'; bp=parent/'build-report.json'; prior=bound(bp)
    generation=ROOT/'build/pride-battle316-generation'; gp=generation/'generation-report.json'
    assert bound(gp)['result']=='GENERATED'
    out=ROOT/'build/pride-battle317';out.mkdir(exist_ok=True)
    cwd=ROOT/'build/pride-sprite-fresh44'
    old=ROOT/'build/pride-hyena-entrance138-generation/hooks'
    changed=[]
    for path in old.glob('*.c'):
        other=generation/'hooks'/path.name
        if digest(path)!=digest(other):changed.append(path.name)
    assert changed==['bankc1_part18_v2.c'],changed
    unit=generation/'hooks'/changed[0]
    diff=list(difflib.unified_diff((old/changed[0]).read_text().splitlines(),unit.read_text().splitlines()))
    assert not [x for x in diff if x.startswith('-') and not x.startswith('---')]
    for pc in ('C14453','C144D8'):assert unit.read_text().count('PrideSceneCompiledPreOpcode(cpu,0x'+pc+'u)')==1
    (out/'generated-unit.diff').write_text('\n'.join(diff)+'\n')
    inputs=argv('link '+(parent/'link.rsp').read_text())[1:]
    previous_unit=bound(ROOT/'build/pride-hyena-voice72/build-report.json')['compiles']['unit']
    with (out/'game-patch.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
    compiles=dict(prior['compiles'])
    for label,template,source,old_object in [
        ('audio',prior['compiles']['audio'],out/'game/tlk_audio.c',ROOT/'build/pride-menu-output83/audio.obj'),
        ('unit',previous_unit,unit,ROOT/'build/pride-hyena-voice72/unit.obj')]:
        cmd=template.copy()
        for flag,value in [('-c',source),('-o',out/(label+'.obj')),('-MT',out/(label+'.obj')),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        if label=='audio':cmd+=['-DTLK_BATTLE_MUSIC_TRIGGER_AVAILABLE=1']
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        match=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old_object]
        assert len(match)==1,(label,match)
        inputs[match[0]]=(out/(label+'.obj')).as_posix();compiles[label]=cmd
        print('compiled',label,flush=True)
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copy2(parent/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    retained=sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())
    assert retained==322 and len(linked)==324
    paths=[Path(__file__),bp,gp,rsp,unit,ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/runner/tlk_audio.h',ROOT/'engine/runner/tlk_battle_music_policy.h',ROOT/'engine/recomp/pride_hooks.json',ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,changed_generated_units=changed,scope='MD Pride battle music command follows actual opening jump. Native waits/gameplay unchanged. Audio history v3; older development audio histories unsupported.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)

if __name__=='__main__':main()
