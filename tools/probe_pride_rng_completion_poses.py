"""Locate the new ordinary route's native fallback pose using read-only evidence."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-rng-player2';observer=base/'allbugs-observer'
    bp=observer/'build-report.json';build=bound(bp)
    assert digest(observer/'player.exe')==build['binary_sha256']
    parent=base/'completion-reference-unpaused2/320'
    tape=base/'controller-unpaused2/route.polled.tape'
    out=base/'completion-pose-probe';out.mkdir()
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_SPRITE_OBJECTS=str(out/'pride-objects.csv'),
               TLK_TRACKED_RAM_LOG=str(out/'route.ram'),TLK_SPRITE_REPORT=str(out/'coverage.json'))
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    cmd=[observer/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
         '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',parent/'resources.ini',
         '--input-polled',tape,'--frames',6000,'--no-pace','--no-audio','--no-record',
         '--config',config,'--wav',out/'route.wav','--wav-seconds',120,
         '--dump-window',out/'window.png','--dump-scene',out/'scene.json']
    with (out/'run.log').open('wb') as log:
        result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    assert result.returncode==0,result.returncode
    baseline=parent/'aot'
    pattern=r'^(frame_sha256|wram_sha256)=([0-9a-f]+)'
    hashes=lambda folder:dict(re.findall(pattern,(folder/'run.log').read_text(),re.M))
    checks=dict(endpoint_neutral=len(hashes(out))==2 and hashes(out)==hashes(baseline),
        whole_pcm_neutral=wav_data(out/'route.wav')==wav_data(baseline/'route.wav'),
        whole_client_neutral=pixels(out/'window.png')==pixels(baseline/'window.png'))
    coverage=json.loads((out/'coverage.json').read_text())
    poses=list(csv.DictReader((out/'pride-objects.csv').open()))
    classified={hex(p):[row for row in poses if int(row['pose'],16)&0x3fffff==p]
                for p in coverage['missing_poses']}
    paths=[Path(__file__),bp,parent/'resources.ini',tape,baseline/'run.log',baseline/'route.wav',baseline/'window.png']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        missing_poses=coverage['missing_poses'],pride_observations_of_missing=classified,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],classified,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
