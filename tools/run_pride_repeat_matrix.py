import argparse
import concurrent.futures
import subprocess
import sys
from audit_scenes import ROOT
from probe_pride_repeat import BASE

CASES=(('snes',256,'native','aot'),('snes',256,'native','lle'),('md',320,'all','aot'),('md',320,'all','lle'),
       ('snes',320,'frames','aot'),('snes',320,'palette','lle'))
WINDOWS=(('snes',256,'native','aot'),('md',320,'all','lle'))


def name(case):return '-'.join(map(str,case))


def capture(case,host):
    start,width,graphics,mode=case;folder=BASE/('scoped-'+host)/name(case);folder.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,str(ROOT/'tools/probe_pride_repeat.py'),'--start',start,'--width',str(width),'--graphics',graphics,
        '--mode',mode,'--output-root',str(folder)]
    if host=='windows':cmd+=['--sdl']
    logs=BASE/'driver-logs';logs.mkdir(exist_ok=True)
    with (logs/('scoped-'+host+'-'+name(case)+'.log')).open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=360)
    print(host,name(case),'PASS',flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('host',choices=('headless','windows'));args=p.parse_args()
    if args.host=='windows':
        for case in WINDOWS:capture(case,args.host)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda c:capture(c,args.host),CASES))


if __name__=='__main__':main()
