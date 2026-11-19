"""Compare completed original Pride scene updates, rather than PPU fields."""
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player';observer=base/'bounce-loop-observer'
    bp=observer/'build-report.json';build=bound(bp)
    assert digest(observer/'player.exe')==build['binary_sha256']
    reference_path=base/'launch-audio-baselines/report.json';assert bound(reference_path)['result']=='PASS'
    out=base/'bounce-loop-audit';out.mkdir();checks={};commands={}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def run(name):
        folder=out/name;folder.mkdir();reference=base/f'launch-audio/{name}-lle'
        command=list(map(str,[observer/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--config',base/'launch-audio/host.ini',
            '--resource-profile',base/f'launch-audio/{name}.ini','--input-polled',ROOT/'engine/tapes/allbugsF.read.tape',
            '--frames',4500,'--lle','--no-pace','--no-audio','--no-record',
            '--hash-at',','.join(map(str,range(1,4501)))]))
        commands[name]=command
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_BOUNCE_LOOP_TRACE=str(folder/'loops.csv'))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=400)
        actual=re.findall(pattern,(folder/'run.log').read_text())
        expected=re.findall(pattern,(reference/'run.log').read_text())
        checks[name+'/observer_neutral_every_field']=len(actual)==4500 and actual==expected
        with (folder/'loops.csv').open() as stream:return list(csv.DictReader(stream))
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={name:pool.submit(run,name) for name in ('native','bounce')}
        runs={name:future.result() for name,future in futures.items()}
    assert all(checks.values()),checks
    columns=('scene','rng','health','x','y','action','timer','death','actors')
    differences={}
    for column in columns:
        rows=[dict(sequence=a['sequence'],native_field=a['field'],bounce_field=b['field'],
            native=a[column] if column!='actors' else None,bounce=b[column] if column!='actors' else None)
            for a,b in zip(runs['native'],runs['bounce']) if a[column]!=b[column]]
        differences[column]=dict(count=len(rows),first=rows[:3],last=rows[-3:])
    paths=[Path(__file__),bp,reference_path,ROOT/'tools/native_bounce_loop_observer.c']
    report=dict(result='OBSERVED',checks=checks,commands=commands,
        original_entry='c08934',loop_counts={n:len(r) for n,r in runs.items()},
        differences=differences,production_changed=False,full_gameplay_equivalence_proven=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Loops',report['loop_counts'],'differences',{c:r['count'] for c,r in differences.items()},flush=True)


if __name__=='__main__':main()
