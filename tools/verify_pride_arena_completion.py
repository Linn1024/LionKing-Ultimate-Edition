"""Retain complete supported Pride route, audio and next-level presentation."""
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_title_preview_history import bound
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def main():
    base=ROOT/'build/pride-arena-work';out=base/'completion';out.mkdir()
    previous_path=ROOT/'build/pride-title-work/completion/report.json';previous=bound(previous_path)
    assert previous['result']=='PASS'
    reference=previous_path.parent/'aot'
    binary=base/'tlk_pride_player.exe';build=json.loads((base/'build-report.json').read_text())
    assert digest(binary)==build['binary_sha256']
    profile=previous_path.parent/'resources.ini';tape=ROOT/'build/pride-rng-player4/width-fight1/best.polled.tape'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
         '--resource-profile',profile,'--config',config,'--input-polled',tape,'--frames',4500,
         '--no-pace','--no-audio','--no-record','--dump-window',out/'window.png','--dump-scene',out/'scene.json',
         '--wav',out/'audio.wav','--wav-seconds',120]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    with (out/'run.log').open('wb') as log:
        subprocess.run(list(map(str,cmd)),cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    scene=json.loads((out/'scene.json').read_text())
    checks=dict(reached_next_level=scene['level']==1,
        gameplay_preserved=hashes(out/'run.log')==hashes(reference/'run.log'),
        complete_audio_preserved=wav_data(out/'audio.wav')==wav_data(reference/'audio.wav'),
        actual_client_preserved=pixels(out/'window.png')==pixels(reference/'window.png'))
    paths=[Path(__file__),base/'build-report.json',binary,previous_path,profile,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=list(map(str,cmd)),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()},full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'complete supported Pride route',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
