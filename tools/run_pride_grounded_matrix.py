"""Execute the isolated early-grounding cases; keep SDL clients serial."""
import argparse
import concurrent.futures
from pathlib import Path
import subprocess
import sys
from audit_scenes import ROOT


def capture(width,graphics,mode,*,checkpoint=False,windows=False,frames=None):
    name=f'{width}-{graphics}-{mode}'
    frames=frames or (5400 if checkpoint else 3000)
    folder='windows/'+('checkpoint-'+name if checkpoint else name+'-'+str(frames)) if windows else ('checkpoint/' if checkpoint else 'default/')+name
    out=ROOT/'build/pride-grounded'/folder;out.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(ROOT/'tools/probe_pride_grounded.py'),'--width',str(width),'--graphics',graphics,
        '--execution',mode,'--frames',str(frames),'--output-root',str(out)]
    if checkpoint:command+=['--route','checkpoint']
    if windows:command+=['--sdl']
    with (out/'driver.log').open('wb') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    print(folder+' PASS',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=('headless','windows','verify'));args=p.parse_args()
    if args.stage=='headless':
        jobs=[(w,g,m,c) for c in (False,True) for w in (256,320) for g in (('native','all') if c else ('native','frames','palette','all')) for m in ('aot','lle')]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(lambda j:capture(*j[:3],checkpoint=j[3]),jobs))
    elif args.stage=='windows':
        cases=[(w,g,f) for w,g in ((256,'native'),(320,'all')) for f in (2053,2076,3000)]
        cases += [(w,g,2071) for w in (256,320) for g in ('frames','palette')]
        for width,graphics,frames in cases:
            for mode in ('aot','lle'):capture(width,graphics,mode,windows=True,frames=frames)
        for width,graphics,mode in ((256,'native','aot'),(320,'all','lle')):capture(width,graphics,mode,windows=True,checkpoint=True)
        subprocess.run([sys.executable,str(ROOT/'tools/verify_pride_grounded_overlap_windows.py')],cwd=ROOT,check=True,timeout=900)
    else:
        subprocess.run([sys.executable,str(ROOT/'tools/finalize_pride_grounded_diagnostics.py')],cwd=ROOT,check=True,timeout=120)
        subprocess.run([str(ROOT/'.tools/python32/python.exe'),str(ROOT/'tools/verify_pride_grounded_cpu.py')],cwd=ROOT,check=True,timeout=120)
        subprocess.run([sys.executable,str(ROOT/'tools/summarize_pride_grounded.py')],cwd=ROOT,check=True,timeout=900)


if __name__=='__main__':main()
