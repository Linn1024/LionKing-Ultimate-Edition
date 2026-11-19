"""Build maintained output-only Pride music ownership on preview53 inputs."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    parent=ROOT/'build/pride-checkpoint-capability53';bp=parent/'build-report.json';prior=bound(bp)
    ap=ROOT/'build/pride-continue-token-behavior50/build-report.json';audio=bound(ap)
    out=ROOT/'build/pride-music-output62';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44';commands={};compiles={}
    patcher=ROOT/'engine/scripts/apply_runtime_patches.py'
    for label,source in [('runtime',ROOT/'engine/snesrecomp'),('game',ROOT/'engine')]:
        cmd=[sys.executable,str(patcher),'--patches',str(ROOT/f'engine/cmake/{label}-patches'),'--snesrecomp',str(source),'--out',str(out/label)]
        commands[label]=cmd
        with (out/(label+'-patch.log')).open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
    owner,=[r for r in rows if r.get('output','').endswith('/tlk_native_audio_owner.c.obj')]
    dsp,=[r for r in rows if r.get('output','').endswith('/tlk-runtime/dsp.c.obj') and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in prior['link_inputs_sha256']]
    original_dsp=Path(dsp['file']);before=original_dsp.read_text();after=(out/'runtime/dsp.c').read_text()
    addition='    if(TlkNativeAudioOwnerMusicMute(i,dsp->echoVolumeL,dsp->echoVolumeR))continue;\n'
    assert after.count(addition)==1 and after.replace(addition,'')==before
    inputs=argv('link '+(parent/'link.rsp').read_text())[1:]
    tasks=[('audio',audio['compiles']['audio'],out/'game/tlk_audio.c',ROOT/'build/pride-continue-token-behavior50/audio.obj'),
           ('owner',argv(owner['command']),ROOT/'engine/runner/tlk_native_audio_owner.c',(cwd/owner['output']).resolve()),
           ('dsp',argv(dsp['command']),out/'runtime/dsp.c',(cwd/dsp['output']).resolve())]
    for label,template,source,old in tasks:
        cmd=template.copy()
        for flag,value in [('-c',source),('-o',out/(label+'.obj')),('-MT',out/(label+'.obj')),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old]
        assert len(indices)==1,(label,indices);inputs[indices[0]]=(out/(label+'.obj')).as_posix();compiles[label]=cmd
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(parent/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==319 and len(linked)==322
    paths=[Path(__file__),bp,ap,rsp,patcher,original_dsp,ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/runner/tlk_audio.h',
           ROOT/'engine/runner/tlk_audio_owner_history.inc',ROOT/'engine/runner/tlk_native_audio_owner.c',ROOT/'engine/runner/tlk_native_audio_owner.h',
           *sorted((ROOT/'engine/cmake/runtime-patches').glob('*.hunks')),*sorted((ROOT/'engine/cmake/game-patches').glob('*.hunks')),
           out/'runtime/dsp.c',out/'game/tlk_audio.c']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),commands=commands,compiles=compiles,link_inputs_sha256=linked,
                unchanged_public_inputs=unchanged,fresh_standalone_graph_claimed=False,guest_rom_code_or_assets_modified=False,
                native_owner_state_size=896,backward_compatibility_implemented=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
