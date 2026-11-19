"""Locate actual width-dependent guest updates without editing the live game."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-player2';observer=base/'allbugs-observer'
    bp=observer/'build-report.json';build=bound(bp)
    assert digest(observer/'player.exe')==build['binary_sha256']
    out=base/'width-diagnosis';out.mkdir()
    profile=base/'completion-reference-unpaused256/256/resources.ini'
    tape=base/'controller-unpaused2/route.polled.tape'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(SDL_VIDEODRIVER='dummy',TLK_TRACKED_RAM_LOG=str(out/'route.ram'),
               TLK_CAMERA_TRACE=str(out/'camera.csv'),TLK_RNG_ENTRY_TRACE=str(out/'entry.csv'))
    cmd=[observer/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
         '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,
         '--input-polled',tape,'--frames',3000,'--no-pace','--no-audio','--no-record',
         '--config',config,'--hash-at',','.join(map(str,range(1,3001)))]
    with (out/'run.log').open('wb') as log:
        result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    assert result.returncode==0,result.returncode
    baseline=base/'completion-reference-unpaused256/256/aot/run.log'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    actual=re.findall(pattern,(out/'run.log').read_text())
    expected=re.findall(pattern,baseline.read_text())[:3000]
    assert len(actual)==3000 and actual==expected,'Observer changed ordinary width256 playback'
    wide=base/'completion-pose-probe/route.ram'
    a=[r.split() for r in wide.read_text().splitlines()][:3000]
    b=[r.split() for r in (out/'route.ram').read_text().splitlines()]
    assert len(a)==len(b)==3000
    def first(columns):
        return next((dict(field=int(x[0]),wide=x,native=y) for x,y in zip(a,b)
                     if any(x[i]!=y[i] for i in columns)),None)
    observations=dict(first_player_difference=first((4,5)),first_rng_difference=first((2,)),
                      first_health_difference=first((3,)),first_life_difference=first((7,)))
    paths=[Path(__file__),bp,profile,tape,baseline,wide,ROOT/'engine/runner/tlk_camera.c',
           ROOT/'engine/runner/tlk_md_camera.c']
    report=dict(result='PASS',observer_full_frame_wram_neutral_every_field=True,
        compared_fields=3000,observations=observations,command=list(map(str,cmd)),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(observations,indent=2),flush=True)


if __name__=='__main__':main()
