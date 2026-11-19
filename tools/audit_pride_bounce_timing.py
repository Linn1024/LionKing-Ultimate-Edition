"""Observe player/RNG/poll state for the existing bounce selection, read-only."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player'
    observer=base/'allbugs-observer';bp=observer/'build-report.json';build=bound(bp)
    assert digest(observer/'player.exe')==build['binary_sha256']
    rp=base/'launch-audio-baselines/report.json';assert bound(rp)['result']=='PASS'
    out=base/'bounce-timing-audit';out.mkdir()
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    checks={};commands={}
    def run(name):
        folder=out/name;folder.mkdir();reference=base/f'launch-audio/{name}-aot'
        command=[str(observer/'player.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
            '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(base/'launch-audio/host.ini'),
            '--resource-profile',str(base/f'launch-audio/{name}.ini'),
            '--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),'--frames','4500',
            '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,4501)))]
        commands[name]=command
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_TRACKED_RAM_LOG=str(folder/'route.ram'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        actual=re.findall(pattern,(folder/'run.log').read_text())
        expected=re.findall(pattern,(reference/'run.log').read_text())
        checks[name+'/every_full_guest_field_observer_neutral']=len(actual)==4500 and actual==expected
        return [line.split() for line in (folder/'route.ram').read_text().splitlines()]
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={name:pool.submit(run,name) for name in ('native','bounce')}
        runs={name:future.result() for name,future in futures.items()}
    assert all(checks.values()),checks
    columns=['field','lag','rng','health','player_x','player_y','level','death_counter','timer']
    differences={}
    for index,column in enumerate(columns):
        rows=[dict(field=int(a[0]),native=a[index],bounce=b[index])
            for a,b in zip(runs['native'],runs['bounce']) if a[index]!=b[index]]
        differences[column]=dict(count=len(rows),first=rows[:5],last=rows[-5:])
    paths=[Path(__file__),bp,rp,ROOT/'tools/build_pride_rng_allbugs.py']
    report=dict(result='OBSERVED',checks=checks,commands=commands,fields=4500,
        observed_columns=columns,differences=differences,production_changed=False,
        full_gameplay_equivalence_proven=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print({name:row['count'] for name,row in differences.items()},flush=True)


if __name__=='__main__':main()
