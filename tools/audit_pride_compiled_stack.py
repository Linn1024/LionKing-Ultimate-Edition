"""Locate private compiled/interpreted revival RAM divergence with native controls.

Diagnostic snapshots and low-WRAM change traces are evidence, not a parity gate.
No guest memory is normalized or rewritten by this driver.
"""
import argparse
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_compiled_windows import saved_wram
from verify_windows import hashes


def frames(path):
    state=bytearray(0x2000)
    with path.open() as stream:
        for frame,changes in itertools.groupby(map(json.loads,stream),key=lambda r:r['f']):
            for r in changes:state[int(r['adr'],16)]=int(r['val'],16)
            yield frame,bytes(state)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frames',type=int,default=4703)
    parser.add_argument('--host',choices=('sdl','headless'),default='sdl')
    parser.add_argument('--variants',nargs='+',choices=('native','owned'),default=['native','owned'])
    parser.add_argument('--hwlog-from',type=int)
    parser.add_argument('--output-root',type=Path,default=Path('build/pride-compiled-revival/stack-audit'))
    args=parser.parse_args();base=ROOT/'build/pride-compiled-revival';out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True)
    binary=base/('compiled-restore-sdl.exe' if args.host=='sdl' else 'compiled-restore.exe');identity=digest(binary)
    assert identity==json.loads((base/('sdl-build-report.json' if args.host=='sdl' else 'build-report.json')).read_text())['binary_sha256']
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = snes\n')
    results={}
    for variant in args.variants:
        runs={}
        for mode in ('aot','lle'):
            folder=out/(variant+'-'+mode);folder.mkdir(exist_ok=True)
            env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):
                env[key]=str(folder)
            for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                        'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO'):
                env[key]=str(int(variant=='owned'))
            env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md')
            trace=folder/'wram.jsonl';trace.unlink(missing_ok=True)
            env['SNESRECOMP_WRAM_TRACE_FILE']=str(trace);env.pop('TLK_WATCH',None)
            if args.hwlog_from is not None:
                env['TLK_HWLOG']=str(folder/'hardware.log');env['TLK_HWLOG_FROM']=str(args.hwlog_from)
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',profile,'--frames',args.frames,
                 '--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
                 '--save-at',args.frames,folder/'snapshot.state']
            if args.host=='sdl':cmd+=['--config',config,'--no-pace','--no-audio','--no-record']
            if mode=='lle':cmd.append('--lle')
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            runs[mode]=dict(guest=hashes(folder/'run.log'),resume_pc=struct.unpack_from('<I',(folder/'snapshot.state').read_bytes(),16)[0],
                artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        a=out/(variant+'-aot');b=out/(variant+'-lle')
        ar,at=saved_wram(a/'snapshot.state',runs['aot']['guest']['wram_sha256'])
        br,bt=saved_wram(b/'snapshot.state',runs['lle']['guest']['wram_sha256'],at)
        differences=[dict(address=f'{n:05x}',aot=x,lle=y) for n,(x,y) in enumerate(zip(ar,br)) if x!=y]
        # Trace logs omit unchanged frames; merge onto the real field clock.
        ai=iter(frames(a/'wram.jsonl'));bi=iter(frames(b/'wram.jsonl'))
        an=next(ai,None);bn=next(bi,None);av=bv=bytes(0x2000);divergent=[]
        for field in range(1,args.frames+1):
            if an and an[0]==field:av=an[1];an=next(ai,None)
            if bn and bn[0]==field:bv=bn[1];bn=next(bi,None)
            if av!=bv:
                diff=[dict(address=f'{n:05x}',aot=x,lle=y) for n,(x,y) in enumerate(zip(av,bv)) if x!=y]
                divergent.append(dict(field=field,differences=diff))
        results[variant]=dict(runs=runs,full_wram_differences=differences,snapshot_wram_offset=at,
            low_wram_divergent_fields=divergent)
        print(variant+': full WRAM differences='+str(len(differences))+'; divergent low-WRAM fields='+str(len(divergent))+
              '; first='+str(divergent[0]['field'] if divergent else None),flush=True)
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='AUDITED',scope=__doc__,runs=results,
        binary_sha256=identity,script_sha256=digest(Path(__file__)),host=args.host,frames=args.frames,variants=args.variants,hwlog_from=args.hwlog_from,
        full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
