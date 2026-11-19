"""Exercise real rejected-load and post-native-success rollback across revival boundaries."""
import argparse
import concurrent.futures
import subprocess
import sys

from audit_scenes import ROOT
from probe_pride_reject_rollback import BASE

CASES=(('snes-default',256,'native',269,273,'aot'),
       ('md-default',320,'all',269,273,'lle'),
       ('snes-default',256,'native',299,300,'lle'),
       ('md-default',320,'all',301,303,'aot'),
       ('snes-checkpoint',256,'native',269,344,'aot'),
       ('snes-checkpoint',320,'all',345,346,'lle'))
WINDOWS=(('snes-default',256,'native',269,273,'lle'),('md-default',320,'all',301,303,'aot'))


def case_name(job):return '-'.join(map(str,job))


def capture(job,host):
    context,width,graphics,save,fault,mode=job;name=case_name(job)
    folder=BASE/host/name;folder.mkdir(parents=True,exist_ok=True)
    variants=['preflight','forced'] if host=='windows' else (['preflight','history','cache','backend','forced'] if job==CASES[0] else ['backend','forced'])
    command=[sys.executable,str(ROOT/'tools/probe_pride_reject_rollback.py'),'--context',context,'--width',str(width),
        '--graphics',graphics,'--save-age',str(save),'--fault-age',str(fault),'--mode',mode,'--variants',*variants,'--output-root',str(folder)]
    if host=='windows':command+=['--sdl']
    logs=BASE/'driver-logs';logs.mkdir(exist_ok=True)
    with (logs/(host+'-'+name+'.log')).open('wb') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
    print(host,name,'PASS',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('host',choices=('headless','windows'));args=p.parse_args()
    if args.host=='windows':
        for case in WINDOWS:capture(case,args.host)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda case:capture(case,args.host),CASES))


if __name__=='__main__':main()
