"""Exercise normal-actor handoff with ordinary held inputs and native controls."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest

BASE=ROOT/'build/pride-actor-handoff'
CONTEXTS={'md-polled':('md','checkpoint','polled',2329,2340),
    'snes-default':('snes','default','frame',2076,2087),
    'md-default':('md','default','frame',2077,2088),
    'snes-checkpoint':('snes','checkpoint','polled',4775,4786)}


def inputs():
    out=BASE/'inputs';out.mkdir(exist_ok=True);sources={};proof={}
    source=ROOT/'build/pride-game-over-music/normal.tape'
    for start,ready,end in (('snes',2076,2087),('md',2077,2088)):
        tape=source.read_bytes()[:1669*2]+bytes((ready-1-1669)*2)+struct.pack('<H',0x100)*(end-ready+1)
        (out/(start+'-default.tape')).write_bytes(tape)
        assert len(tape)==end*2
        proof[start+'-default']=dict(input_kind='frame',right_from_field=ready,raw_right_word=256,prefix_frames=ready-1)
    reference=ROOT/'build/pride-spawn-revival/checkpoint/snes-320-native-lle'
    rows=[r.split() for r in (reference/'route.ram').read_text().splitlines()]
    polls=int(re.search(r'polls_seen=(\d+)',(reference/'run.log').read_text())[1])
    assert sum(r[1]=='0' for r in rows)==polls
    assert next(r for r in rows if int(r[0])==4775)[1]=='0'
    cut=sum(r[1]=='0' for r in rows if int(r[0])<4775)
    source_polled=ROOT/'build/pride-health-death-native/neutral-tail.polled.tape';original=source_polled.read_bytes()
    assert cut==4104 and cut*2<len(original)
    tape=original[:cut*2]+struct.pack('<H',0x100)*((len(original)//2)-cut+1000)
    (out/'snes-checkpoint.polled.tape').write_bytes(tape);assert tape[:cut*2]==original[:cut*2]
    proof['snes-checkpoint']=dict(input_kind='polled',right_from_poll=cut+1,expected_ready_field=4775,
        prefix_words=cut,total_baseline_polls=polls,one_poll_per_nonlag_field_proved=True,raw_right_word=256)
    for p in (Path(__file__),source,source_polled,reference/'route.ram',reference/'run.log'):
        sources[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    (out/'provenance.json').write_text(json.dumps(dict(result='ORDINARY_INPUTS_AUTHORED',cases=proof,source_sha256=sources,
        artifacts_sha256={p.name:digest(p) for p in out.glob('*.tape')},loaded_states=False,guest_fixture_edits=False),indent=2)+'\n')


def capture(context,width,graphics,mode,presenter='owned',host='probe',field=None,in_place=False):
    start,route,kind,ready,end=CONTEXTS[context];field=field or end
    name=f'{context}-{width}-{graphics}-{mode}-{presenter}'+(f'-{field}-'+('in-place' if in_place else 'edges') if host=='sdl' else '')
    folder=BASE/('windows' if host=='sdl' else 'active')/name;folder.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,str(ROOT/'tools/probe_pride_actor_handoff.py'),'--start',start,'--route',route,'--width',str(width),
        '--graphics',graphics,'--execution',mode,'--presenter',presenter,'--frames',str(field),'--output-root',str(folder)]
    if context!='md-polled':
        path=BASE/'inputs'/(context+('.polled.tape' if kind=='polled' else '.tape'))
        command+=['--input-file',str(path),'--input-kind',kind]
    if host=='sdl':command+=['--sdl']
    if in_place:command+=['--hud-in-place']
    logs=BASE/'driver-logs';logs.mkdir(exist_ok=True)
    with (logs/(name+'.log')).open('wb') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    print(name+' PASS',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',choices=('inputs','headless','windows','neutral'));args=p.parse_args()
    BASE.mkdir(exist_ok=True)
    if args.stage=='inputs':inputs()
    elif args.stage=='headless':
        jobs=[(c,w,g,m,'owned') for c in CONTEXTS for w in (256,320) for g in ('native','frames','palette','all') for m in ('aot','lle')]
        jobs += [(c,w,g,'aot','native') for c in CONTEXTS for w in (256,320) for g in ('native','frames','palette','all')]
        jobs += [('md-polled',320,g,m,'owned') for g in ('cub','hud') for m in ('aot','lle')]
        jobs += [('md-polled',320,g,'aot','native') for g in ('cub','hud')]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda j:capture(*j),jobs))
    elif args.stage=='windows':
        # Actual former-failure point, post-guard continuation and both HUD options.
        for field in (2331,2340):
            for graphics in ('native','frames','palette'):
                for mode in ('aot','lle'):capture('md-polled',320,graphics,mode,host='sdl',field=field)
                capture('md-polled',320,graphics,'aot','native','sdl',field)
        for context in ('snes-default','md-default','snes-checkpoint'):
            for width,graphics in ((256,'native'),(320,'all')):
                for mode in ('aot','lle'):capture(context,width,graphics,mode,host='sdl')
                capture(context,width,graphics,'aot','native','sdl')
        for mode in ('aot','lle'):capture('md-polled',320,'native',mode,host='sdl',field=2331,in_place=True)
        for graphics in ('cub','hud'):
            for mode in ('aot','lle'):capture('md-polled',320,graphics,mode,host='sdl')
            capture('md-polled',320,graphics,'aot','native','sdl')
    else:
        jobs=[]
        for start in ('snes','md'):
            for width,graphics in ((256,'native'),(320,'all')):
                for mode in ('aot','lle'):jobs.append((start,width,graphics,mode,'default',3000))
        jobs += [('snes',256,'native','aot','checkpoint',5400),('snes',320,'all','lle','checkpoint',5400)]
        def neutral(j):
            start,width,graphics,mode,route,frames=j;folder=BASE/'neutral'/f'{start}-{width}-{graphics}-{mode}-{route}';folder.mkdir(parents=True,exist_ok=True)
            command=[sys.executable,str(ROOT/'tools/probe_pride_actor_handoff.py'),'--start',start,'--width',str(width),'--graphics',graphics,
                '--execution',mode,'--route',route,'--frames',str(frames),'--output-root',str(folder)]
            logs=BASE/'driver-logs';logs.mkdir(exist_ok=True)
            with (logs/(folder.name+'.log')).open('wb') as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            print('neutral/'+folder.name+' PASS',flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(neutral,jobs))


if __name__=='__main__':main()
