"""Replay an actual private controller save in a fresh process.

This first harness covers post-preparation checkpoint continuation, not prepared
graphics or all scene lifecycle contexts. Source/binary data remain explicit.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes


def rows(path):
    with path.open() as f:return list(csv.DictReader(f))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save-at',type=int,default=4703)
    parser.add_argument('--output-root',type=Path,default=Path('build/pride-scene-state/pilot'))
    parser.add_argument('--save-mode',choices=('aot','lle'),default='aot')
    parser.add_argument('--load-mode',choices=('aot','lle'),default='aot')
    args=parser.parse_args();out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True)
    base=ROOT/'build/pride-scene-state';binary=base/'scene-state-probe.exe';build_path=base/'build-report.json'
    build=json.loads(build_path.read_text());assert digest(binary)==build['runs']['probe']['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    identities={str(build_path.relative_to(ROOT)).replace('\\','/'):digest(build_path),
                str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__))}
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = snes\n')
    neutral=base/'neutral.polled.tape';assert neutral.read_bytes()==bytes(4096)
    state=out/'checkpoint.private-state';results={}
    for name,load in (('baseline',False),('resumed',True)):
        folder=out/name;folder.mkdir(exist_ok=True);env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--frames','5400','--input-polled',neutral if load else ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
             '--ram-log',folder/'route.ram','--dump-png',folder/'picture.png']
        if load:cmd+=['--load',state]
        else:cmd+=['--save-at',args.save_at,state]
        if (args.load_mode if load else args.save_mode)=='lle':cmd.append('--lle')
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        results[name]=dict(exit_code=result.returncode,guest=hashes(folder/'run.log'),
            artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        print(name,'exit',result.returncode,flush=True)
    exact=results['baseline']['exit_code']==results['resumed']['exit_code']==0 and results['baseline']['guest']==results['resumed']['guest']
    tracked=False;events=False
    if exact:
        a=(out/'baseline/route.ram').read_bytes().splitlines(keepends=True)
        b=(out/'resumed/route.ram').read_bytes().splitlines(keepends=True)
        tracked=b==a[-len(b):] and len(b)==5400-args.save_at
        expected=[r for r in rows(out/'baseline/owner-events.csv') if int(r['field'])>args.save_at]
        events=rows(out/'resumed/owner-events.csv')==expected
    for name,sha in identities.items():assert digest(ROOT/name)==sha,name
    report=dict(result='AUDITED',scope=__doc__,runs=results,save_at=args.save_at,save_mode=args.save_mode,load_mode=args.load_mode,
        endpoint_guest_exact=exact,remaining_tracked_ram_exact=tracked,remaining_owner_events_exact=events,
        state_sha256=digest(state) if state.exists() else None,binary_sha256=digest(binary),source_sha256=identities,
        prepared_graphics_verified=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('New-process endpoint exact='+str(exact)+'; tracked RAM='+str(tracked)+'; owner events='+str(events),flush=True)


if __name__=='__main__':main()
