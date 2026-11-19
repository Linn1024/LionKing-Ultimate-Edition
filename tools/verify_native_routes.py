"""Windows AOT/LLE regression routes; does not claim external emulator sync."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--allbugs',action='store_true');ap.add_argument('--workers',type=int,default=4)
    ap.add_argument('--binary',type=Path,default=ROOT/'engine/build-win/tlk_headless.exe')
    ap.add_argument('--output',type=Path,default=ROOT/'build/native-route-verification')
    args=ap.parse_args();dest=ROOT/args.output;dest.mkdir(parents=True,exist_ok=True)
    binary=(ROOT/args.binary).resolve()
    identity=hashlib.sha256(binary.read_bytes()).hexdigest()
    script_identity=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (dest/('allbugs-report.json' if args.allbugs else 'play-report.json')).write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    if args.allbugs:
        routes=[('allbugs',60648,ROOT/'engine/tapes/allbugsF.read.tape',True)]
    else:
        routes=[(p.stem,5000,p,p.name.endswith('.polled.tape')) for p in sorted((ROOT/'engine/build/playtapes').glob('*.tape'))]
        assert len(routes)>=70,'local play-tape set incomplete'
        routes += [('idle600',600,None,False),('idle3000',3000,None,False),('idle12000',12000,None,False),
                   ('speedrun1200',1200,ROOT/'engine/tapes/6987M.read.tape',True),
                   ('speedrun6000',6000,ROOT/'engine/tapes/6987M.read.tape',True)]
    def run(item):
        route,mode=item;name,frames,tape,polled=route;stem=dest/f'{name}-{mode}'
        command=[str(binary),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--frames',str(frames)]
        if tape:command+=['--input-polled' if polled else '--input',str(tape)]
        if mode=='lle':command+=['--lle']
        if args.allbugs:command+=['--ram-log',str(stem)+'.ram']
        with stem.with_suffix('.log').open('wb') as output:
            subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=1200)
        text=stem.with_suffix('.log').read_text(errors='replace')
        hashes=dict(re.findall(r'^(frame_sha256|wram_sha256)=([0-9a-f]+)',text,re.M))
        assert len(hashes)==2,(name,mode,text[-1000:])
        return name,mode,hashes
    modes={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(run,(route,mode)) for route in routes for mode in ('aot','lle')]
        for future in concurrent.futures.as_completed(futures):
            name,mode,value=future.result();modes.setdefault(name,{})[mode]=value
            if len(modes[name])==2:
                assert modes[name]['aot']==modes[name]['lle'],name+' guest hashes differ'
                print(name,'MATCH frame and full WRAM',flush=True)
    if args.allbugs:
        assert (dest/'allbugs-aot.ram').read_bytes()==(dest/'allbugs-lle.ram').read_bytes(),'All Bugs tracked RAM differs'
    report={'result':'PASS','scope':__doc__,'route_count':len(routes),'routes':modes,
            'allbugs_tracked_ram_equal_every_frame':args.allbugs,
            'binary_sha256':identity,'verifier_sha256':script_identity}
    assert hashlib.sha256(binary.read_bytes()).hexdigest()==identity
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==script_identity
    (dest/('allbugs-report.json' if args.allbugs else 'play-report.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(len(routes),'native AOT/LLE routes PASS',flush=True)

if __name__=='__main__':main()
