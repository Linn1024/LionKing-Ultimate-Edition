"""Audit private compiled revival PCM against the interpreter on the full route."""
import json
import os
from pathlib import Path
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes


def main():
    base=ROOT/'build/pride-compiled-revival';out=base/'sync-audio';out.mkdir(exist_ok=True)
    binary=base/'compiled-restore-sdl.exe';identity=digest(binary)
    build=base/'sdl-build-report.json';assert identity==json.loads(build.read_text())['binary_sha256']
    sources={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__)),
             str(build.relative_to(ROOT)).replace('\\','/'):digest(build),
             'engine/runner/sdl_main.c':digest(ROOT/'engine/runner/sdl_main.c')}
    assert '#define NTSC_FPS (21477272.0 / 357366.0)' in (ROOT/'engine/runner/sdl_main.c').read_text()
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = snes\n')
    (out/'report.json').write_text('{"result":"RUNNING"}\n');results={}
    pcm={}
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir(exist_ok=True);env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):
            env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_WATCH',None)
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',config,'--resource-profile',profile,'--frames','5400','--no-pace','--no-audio','--no-record',
             '--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
             '--wav',folder/'audio.wav','--wav-seconds','120']
        if mode=='lle':cmd.append('--lle')
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        with wave.open(str(folder/'audio.wav'),'rb') as wav:
            params=wav.getparams();pcm[mode]=wav.readframes(params.nframes)
        assert params.nframes==5400*params.framerate*357366//21477272,'PCM must cover all5400 NTSC host fields'
        assert pcm[mode] and any(pcm[mode])
        results[mode]=dict(guest=hashes(folder/'run.log'),wav_parameters=list(params),
            artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        print(mode+': complete5400-frame PCM captured',flush=True)
    same=pcm['aot']==pcm['lle'];guest=results['aot']['guest']==results['lle']['guest']
    first=next((n for n,(a,b) in enumerate(zip(pcm['aot'],pcm['lle'])) if a!=b),None)
    for name,sha in sources.items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='PASS' if same and guest else 'AUDITED',scope=__doc__,runs=results,
        binary_sha256=identity,source_sha256=sources,pcm_exact=same,guest_hashes_exact=guest,
        first_different_pcm_byte=first,pcm_bytes={k:len(v) for k,v in pcm.items()},
        full_route_host_frames=5400,full_route_duration_verified=True,
        original_md_audio_phase_verified=False,production_behavior_enabled=False,full_first_level_fidelity_complete=False),indent=2)+'\n')
    print('Full route PCM exact='+str(same)+'; endpoint guest hashes exact='+str(guest),flush=True)


if __name__=='__main__':main()
