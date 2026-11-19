"""Relink native queue-preserving menu effects and verified slot/voice ownership."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    parent=ROOT/'build/pride-menu-audio80';bp=parent/'build-report.json';prior=bound(bp)
    owner_report=ROOT/'build/pride-music-output65/build-report.json';owner=bound(owner_report)
    proofs=[ROOT/'build/pride-menu-output83-owner-component/report.json',ROOT/'build/pride-menu-output83-controller/report.json',ROOT/'build/pride-menu-spc82/report.json']
    for p in proofs:assert bound(p)['result'] in ('PASS','NEUTRAL_MENU_SPC_OBSERVER')
    out=ROOT/'build/pride-menu-output83';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    cmd=[sys.executable,str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')]
    with (out/'game-patch.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    inputs=argv('link '+(parent/'link.rsp').read_text())[1:];compiles=dict(prior['compiles'])
    tasks=[('audio',prior['compiles']['audio'],out/'game/tlk_audio.c',parent/'audio.obj'),
           ('resources',prior['compiles']['resources'],out/'game/tlk_resources.c',parent/'resources.obj'),
           ('owner',owner['compiles']['owner'],ROOT/'engine/runner/tlk_native_audio_owner.c',owner_report.parent/'owner.obj')]
    for label,template,source,old in tasks:
        cmd=template.copy()
        for flag,value in [('-c',source),('-o',out/(label+'.obj')),('-MT',out/(label+'.obj')),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1
        inputs[indices[0]]=(out/(label+'.obj')).as_posix();compiles[label]=cmd;print('compiled',label,flush=True)
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copy2(parent/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==319 and len(linked)==322
    paths=[Path(__file__),bp,owner_report,*proofs,rsp,ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/runner/tlk_resources.c',ROOT/'engine/runner/tlk_menu_audio_policy.h',ROOT/'engine/runner/tlk_native_audio_owner.c',out/'game/tlk_audio.c',out/'game/tlk_resources.c']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,
                unchanged_candidate80_inputs=unchanged,menu_native_queue_preserved=True,current_owner_schema=3,
                original_game_instructions_or_assets_modified=False,fresh_full_graph_claimed=False,published=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
