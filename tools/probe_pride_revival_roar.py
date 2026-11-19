"""Audit an isolated zero-roar publication choice against original MD counters.

Uses the existing semantic publication event, not per-field RAM masking. The
native recovery code keeps running; mismatches remain evidence for next work.
"""
import csv
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--watch',action='store_true',help='Log actual native opcodes writing the roar counter')
    args=parser.parse_args()
    out=ROOT/'build/pride-revival-roar';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text('{"result":"RUNNING"}\n')
    binary=ROOT/'engine/build-win/tlk_scene_restore_probe.exe';identity=digest(binary)
    oracle_path=ROOT/'build/pride-checkpoint-player/md-restored-widget-counters/report.json'
    oracle=json.loads(oracle_path.read_text());assert oracle['result']=='PASS'
    expected={r['age']:r for r in oracle['fields']}
    source_paths=[Path(__file__),ROOT/'tools/pride_scene_restore_probe.c',ROOT/'tools/pride_scene_owner_probe.c',
        ROOT/'tools/pride_scene_prepare_probe.c',ROOT/'tools/pride_scene_template.h',ROOT/'tools/pride_native_bank_probe.c',
        ROOT/'engine/runner/tlk_death_scene.c',ROOT/'engine/runner/tlk_death_scene.h',oracle_path,
        ROOT/'build/pride-death-phases/native.ini',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape']
    identities={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in source_paths}
    results={}
    for mode in ('native','zero'):
        folder=out/mode;folder.mkdir(exist_ok=True)
        env=os.environ.copy()
        for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE'):
            env[key]=str(folder)
        for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                    'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL'):env[key]='1'
        env['TLK_SCENE_RESTORE_ROAR_ZERO']='1' if mode=='zero' else '0'
        if args.watch:env['TLK_WATCH']='0x2002'
        else:env.pop('TLK_WATCH',None)
        env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',ROOT/'build/pride-death-phases/native.ini','--lle','--frames','5400',
             '--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
             '--ram-log',folder/'route.ram','--dump-png',folder/'picture.png']
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
        assert digest(binary)==identity
        states=list(csv.DictReader((folder/'restore-fields.csv').open()))
        events=list(csv.DictReader((folder/'restore-events.csv').open()))
        publication=[r for r in events if r['event']=='publish']
        requests=[r for r in events if r['event']=='request_roar']
        assert len(publication)==len(requests)==1
        assert int(publication[0]['age'])==270 and int(requests[0]['age'])==225
        assert int(publication[0]['roar'])==(0 if mode=='zero' else 24)
        if mode=='native':
            previous=ROOT/'build/pride-scene-restore-headless/native-canonical'
            assert hashes(folder/'run.log')==hashes(previous/'run.log')
            assert (folder/'route.ram').read_bytes()==(previous/'route.ram').read_bytes()
            results[mode]=dict(previous_canonical_guest_and_full_tracked_ram_exact=True)
        else:
            differences=[];transitions=[];last=None
            for row in states:
                age=int(row['age']);actual=int(row['roar'])
                if actual!=last:transitions.append(dict(age=age,roar=actual));last=actual
                if age in expected and actual!=expected[age]['roar']:
                    differences.append(dict(age=age,actual=actual,original_md=expected[age]['roar']))
            assert states and max(int(r['age']) for r in states)>=645
            results[mode]=dict(semantic_publication_roar_zero=True,observed_fields=len(states),
                actual_recovery_transitions=transitions,first_difference=differences[0] if differences else None,
                differing_counter_fields=len(differences),original_md_counter_sequence_exact=not differences)
        results[mode]['artifacts_sha256']={p.name:digest(p) for p in folder.iterdir() if p.is_file()}
    for name,sha in identities.items():assert digest(ROOT/name)==sha,name
    report=dict(result='AUDITED',scope=__doc__,probe_sha256=identity,runs=results,
        native_opcode_counter_watch=args.watch,
        per_field_guest_ram_masking=False,production_behavior_enabled=False,renderer_integration=False,
        full_first_level_fidelity_complete=False,source_sha256=identities)
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    summary={key:value for key,value in results['zero'].items() if key!='artifacts_sha256'}
    print('Native control exact; semantic zero-roar experiment: '+json.dumps(summary),flush=True)


if __name__=='__main__':main()
