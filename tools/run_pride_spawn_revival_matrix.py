"""Capture independent initial-position choices; keep actual SDL clients serial.

The alternate MD polled input is a default death, not a checkpoint proof.
"""
import argparse
import concurrent.futures
import subprocess
import sys
from audit_scenes import ROOT


def capture(start,width,graphics,mode,*,checkpoint=False,alternate=False,windows=False,frames=None,in_place=False):
    frames=frames or (5400 if checkpoint else 2329 if alternate else 3000)
    name=f'{start}-{width}-{graphics}-{mode}'
    group='checkpoint' if checkpoint else 'alternate' if alternate else 'default'
    folder=(('overlap/' if in_place else 'windows/')+group+'-'+name+'-'+str(frames)) if windows else group+'/'+name
    base=ROOT/'build/pride-spawn-revival';out=base/folder;out.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(ROOT/'tools/probe_pride_spawn_revival.py'),'--start',start,'--width',str(width),
        '--graphics',graphics,'--execution',mode,'--frames',str(frames),'--output-root',str(out)]
    if checkpoint or alternate:command+=['--route','checkpoint']
    if windows:command+=['--sdl']
    # Probe's default SDL HUD is at edges. Explicit overlap runs use a separate
    # helper below, without racing a generated config or changing guest input.
    assert not in_place
    logs=base/'driver-logs';logs.mkdir(exist_ok=True)
    with (logs/(folder.replace('/','-')+'.log')).open('wb') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    print(folder+' PASS',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=('headless','windows'));args=p.parse_args()
    if args.stage=='headless':
        jobs=[(s,w,g,m,False,False) for s in ('snes','md') for w in (256,320) for g in ('native','frames','palette','all') for m in ('aot','lle')]
        jobs += [('snes',w,g,m,True,False) for w in (256,320) for g in ('native','all') for m in ('aot','lle')]
        jobs += [('md',w,g,m,False,True) for w,g in ((256,'native'),(320,'all')) for m in ('aot','lle')]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(lambda j:capture(*j[:4],checkpoint=j[4],alternate=j[5]),jobs))
    else:
        cases=[(w,g,f) for w,g in ((256,'native'),(320,'all')) for f in (2054,2077,3000)]
        cases += [(w,g,2072) for w in (256,320) for g in ('frames','palette')]
        for width,graphics,frames in cases:
            for mode in ('aot','lle'):capture('md',width,graphics,mode,windows=True,frames=frames)
        for width,graphics,frames in ((256,'native',2053),(320,'all',3000)):
            for mode in ('aot','lle'):capture('snes',width,graphics,mode,windows=True,frames=frames)
        for width,graphics,mode in ((256,'native','aot'),(320,'all','lle')):
            capture('snes',width,graphics,mode,checkpoint=True,windows=True)
            capture('md',width,graphics,mode,alternate=True,windows=True)
        subprocess.run([sys.executable,str(ROOT/'tools/verify_pride_spawn_revival_overlap_windows.py')],cwd=ROOT,check=True,timeout=900)


if __name__=='__main__':main()
