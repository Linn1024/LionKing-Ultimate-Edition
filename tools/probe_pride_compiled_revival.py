"""Compare current private revival ownership in AOT and interpreter execution.

AUDITED reports retain missing hooks/divergence instead of claiming compiled
support from the executable name or from unrelated compiled entries.
"""
import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def rows(p):return list(csv.DictReader(p.open())) if p.exists() else []


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path,default=Path('build/pride-compiled-revival/pilot'))
    parser.add_argument('--binary',type=Path,default=Path('engine/build-win/tlk_scene_restore_probe.exe'))
    args=parser.parse_args();out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True)
    binary=ROOT/args.binary;identity=digest(binary)
    sources=[Path(__file__),ROOT/'tools/pride_scene_restore_probe.c',ROOT/'tools/pride_scene_owner_probe.c',
             ROOT/'tools/pride_scene_prepare_probe.c',ROOT/'tools/pride_scene_template.h',ROOT/'tools/pride_native_bank_probe.c',
             ROOT/'engine/runner/tlk_game.c',ROOT/'engine/runner/aot_pace.h',ROOT/'engine/runner/tlk_guest.c',
             ROOT/'build/pride-health-death-native/neutral-tail.polled.tape']
    identities={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources}
    provenance={}
    if binary==ROOT/'build/pride-compiled-revival/compiled-restore.exe':
        for name in ('generation-report.json','build-report.json'):
            p=binary.parent/name;provenance[name]=digest(p)
        build=json.loads((binary.parent/'build-report.json').read_text())
        assert build['binary_sha256']==identity
        for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    results={}
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir(exist_ok=True)
        env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):
            env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO'):env[key]='1'
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md')
        env.pop('TLK_WATCH',None)
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',ROOT/'build/pride-death-phases/native.ini','--frames','5400',
             '--input-polled',sources[-1],'--ram-log',folder/'route.ram','--dump-png',folder/'picture.png']
        if mode=='lle':cmd.append('--lle')
        with (folder/'run.log').open('wb') as log:
            process=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        assert digest(binary)==identity
        for name,sha in identities.items():assert digest(ROOT/name)==sha,name
        owner=rows(folder/'owner-events.csv');restore=rows(folder/'restore-events.csv')
        statistics=re.search(r'pride_compiled_hook_calls=(\d+) callbacks=(\d+) redirects=(\d+) paired_services=(\d+)',
                             (folder/'run.log').read_text(errors='replace'))
        results[mode]=dict(exit_code=process.returncode,guest=hashes(folder/'run.log'),
            compiled_hooks=dict(zip(('calls','callbacks','redirects','paired_services'),map(int,statistics.groups()))) if statistics else {},
            owner_events=len(owner),restore_events=len(restore),
            begin_fields=[int(r['field']) for r in owner if r['event']=='begin'],
            health_publication_ages=[int(r['age']) for r in restore if r['event']=='publish'],
            normal_fields=[int(r['field']) for r in owner if r['event']=='normal'],
            zero_roar_ready_writers=[r for r in restore if r['event']=='retain_zero_roar_ready'],
            artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
    assert results['lle']['exit_code']==0 and results['lle']['health_publication_ages']==[270]
    same=results['aot']['exit_code']==0 and results['aot']['guest']==results['lle']['guest'] and \
         (out/'aot/route.ram').read_bytes()==(out/'lle/route.ram').read_bytes()
    owner_exact=rows(out/'aot/owner-events.csv')==rows(out/'lle/owner-events.csv')
    restore_exact=rows(out/'aot/restore-events.csv')==rows(out/'lle/restore-events.csv')
    controller_exact=same and owner_exact and restore_exact and \
        results['aot']['compiled_hooks'].get('paired_services',0)>0 and \
        results['aot']['begin_fields']==[4430] and results['aot']['normal_fields']==[4775]
    result=dict(result='AUDITED',scope=__doc__,probe_sha256=identity,runs=results,
        build_provenance_sha256=provenance,
        owner_events_exact=owner_exact,restore_events_exact=restore_exact,
        compiled_controller_trace_exact=controller_exact,
        aot_and_lle_full_tracked_ram_exact=same,compiled_ownership_verified=False,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False,source_sha256=identities)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Revival execution pilot: '+json.dumps({m:{k:v for k,v in r.items() if k not in ('guest','artifacts_sha256','zero_roar_ready_writers')} for m,r in results.items()})+
          '; full tracked RAM exact='+str(same),flush=True)


if __name__=='__main__':main()
