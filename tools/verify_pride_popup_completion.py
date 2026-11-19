"""Play the supported mixture through Pride Lands with the new popup enabled."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def main():
    base=ROOT/'build/pride-popup-work';out=base/'completion';out.mkdir()
    bp=base/'commands4.json';build=json.loads(bp.read_text())
    binary=base/'player/native-engine/tlk_pride_player.exe';assert digest(binary)==build['binary_sha256']
    tape=ROOT/'build/pride-rng-player4/width-fight1/best.polled.tape'
    original_profile=ROOT/'build/pride-scene-template-work/player/launch-completion.ini'
    profile=out/'resources.ini';profile.write_text(original_profile.read_text()+'\ngraphics.sprites.effects.pickup_arrival = md\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands={};results={};checks={}
    previous=ROOT/'build/pride-scene-template-work/player/native-engine/tlk_pride_player.exe'
    for mode in ('previous','aot','lle'):
        folder=out/mode;folder.mkdir()
        env=dict(clean,TLK_SPRITE_REPORT=str(folder/'sprites.json'))
        cmd=[previous if mode=='previous' else binary,'--rom',ROOT/'Lion King, The (USA).sfc',
             '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',original_profile if mode=='previous' else profile,
             '--config',config,'--input-polled',tape,'--frames',4500,'--no-pace','--no-audio','--no-record',
             '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json','--wav',folder/'audio.wav','--wav-seconds',120]
        if mode=='lle':cmd+=['--lle']
        commands[mode]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[mode],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300,check=True)
        scene=json.loads((folder/'scene.json').read_text())
        results[mode]=dict(level=scene['level'],hashes=hashes(folder/'run.log'),
                           coverage=json.loads((folder/'sprites.json').read_text()))
        checks[mode+'/reached_next_main_level']=scene['level']==1
        checks[mode+'/guest_hashes_present']=len(results[mode]['hashes'])==2
        print(mode,'final level',scene['level'],flush=True)
    for mode in ('aot','lle'):
        checks[mode+'/native_gameplay_preserved']=results[mode]['hashes']==results['previous']['hashes']
        checks[mode+'/whole_audio_preserved']=wav_data(out/mode/'audio.wav')==wav_data(out/'previous/audio.wav')
        checks[mode+'/post_level_client_preserved']=pixels(out/mode/'window.png')==pixels(out/'previous/window.png')
    paths=[Path(__file__),bp,tape,original_profile,binary,previous]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=results,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
                full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'completion checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
