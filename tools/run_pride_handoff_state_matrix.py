"""Exercise real revival saves across default preparation and normal publication."""
import argparse
import concurrent.futures
import subprocess
import sys

from audit_scenes import ROOT
from probe_pride_handoff_state import BASE
from run_pride_actor_handoff_matrix import CONTEXTS


def cases(host):
    if host=='headless':
        jobs=[]
        for context,width,graphics,save,load in (
            ('snes-default',256,'native','aot','lle'),('md-default',320,'all','lle','aot')):
            jobs.extend((context,width,graphics,age,save,load) for age in (0,254,267,269,273,274,299,300,301,303))
        for graphics in ('cub','hud'):
            jobs.extend(('md-polled',320,graphics,age,'aot','lle') for age in (300,301))
        jobs.extend(('snes-checkpoint',256,'native',age,'lle','aot') for age in (0,238,269,270,344,345,346,348))
        jobs.extend(('snes-checkpoint',320,'all',age,'aot','lle') for age in (0,269,345,346))
        return jobs
    return [('snes-default',256,'native',age,'aot','lle') for age in (0,268,301)]+[
        ('md-default',320,'all',age,'lle','aot') for age in (0,274,300,302)]+[
        ('md-polled',320,'native',301,'aot','lle'),('md-polled',320,'cub',301,'lle','aot'),
        ('md-polled',320,'hud',300,'aot','lle'),('snes-checkpoint',256,'native',346,'lle','aot'),
        ('snes-checkpoint',320,'all',345,'aot','lle')]


def case_name(job):
    context,width,graphics,age,save,load=job
    return f'{context}-{width}-{graphics}-{age}-{save}-{load}'


def capture(job,host):
    context,width,graphics,age,save,load=job
    ready=345 if context=='snes-checkpoint' else 300
    at=CONTEXTS[context][3]-ready+age
    name=case_name(job);folder=BASE/host/name;folder.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(ROOT/'tools/probe_pride_handoff_state.py'),'--context',context,'--width',str(width),
        '--graphics',graphics,'--save-at',str(at),'--save-mode',save,'--load-mode',load,'--output-root',str(folder)]
    if host=='windows':command+=['--sdl']
    logs=BASE/'driver-logs';logs.mkdir(exist_ok=True)
    with (logs/(host+'-'+name+'.log')).open('wb') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=360)
    print(host,name,'PASS',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('host',choices=('headless','windows'));args=p.parse_args()
    if args.host=='windows':
        for job in cases(args.host):capture(job,args.host)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda job:capture(job,args.host),cases(args.host)))


if __name__=='__main__':main()
