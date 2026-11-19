"""Bind original RNG lifecycle evidence and the uninstalled owned component."""
import csv
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_rng_audit import snes_step
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-lifecycle';bp=base/'build-report.json';build=bound(bp);checks={};paths=[Path(__file__),bp]
    assert digest(base/'observer.exe')==build['binary_sha256']
    for name,sha in build['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    checks['installed_headless_unchanged']=digest(ROOT/'engine/build-win/tlk_headless.exe')==build['installed_headless_sha256']
    for name in ('native/report.json','native-default/report.json','md/report.json','md-default/report.json','component2/report.json'):
        path=base/name;r=bound(path);paths.append(path);assert r['result'] in ('PASS','CAPTURED')
        for key,value in r.get('checks',{}).items():checks[name+'/'+key]=value
    # Cover all observed MD writes to the seed, including the previously missed
    # explicit per-normal-entry assignment at1D77D6..1D77F6.
    reseeds={};rng_calls={}
    for name,folder in (('completion',base/'md/completion'),('checkpoint',base/'md/checkpoint'),('continue',base/'md/continue'),('default',base/'md-default/default')):
        rows=list(csv.DictReader((folder/'rng.csv').open()));expected=0;normal=[];calls=0
        for row in rows:
            seed=int(row['seed'],16);assert seed==expected,(name,row,hex(expected))
            pc=int(row['pc'],16);address=int(row['address'],16);value=int(row['value'],16)
            if row['type']=='4':
                width=int(row['width'])
                for i in range(width):
                    at=address+i
                    if 0xff81ad<=at<=0xff81af:
                        shift=(0xff81af-at)*8;byte=value>>((width-1-i)*8)&255;expected=(expected&~(255<<shift))|byte<<shift
                if pc==0x1d77fe:assert seed==0xaa0b4c;normal.append(int(row['field']))
            elif address==0xb28:calls+=1
        reseeds[name]=normal;rng_calls[name]=calls;checks[name+'/all_md_seed_writes_accounted']=True
    checks['md_normal_bonus_nextlevel_reseed']=reseeds['completion']==[1328,4410,5016]
    checks['md_checkpoint_revival_carries_seed']=reseeds['checkpoint']==[1328]
    checks['md_default_revival_carries_seed']=reseeds['default']==[1328]
    checks['md_continue_yes_reseeds']=reseeds['continue']==[1328,15628]
    normal=[];native_calls=0
    for name,folder in (('completion',base/'native/completion'),('checkpoint',base/'native/checkpoint'),('continue',base/'native/continue'),('default',base/'native-default/default')):
        rows=list(csv.DictReader((folder/'rng.csv').open()));seed=None;clears=[]
        for row in rows:
            actual=int(row['seed'],16);pc=row['pc']
            if pc in ('c080f2','c080f6','c080fa'):seed=actual
            elif pc=='c07973':assert actual==seed&0xffff00;seed=actual
            else:
                assert actual==seed,(name,row,hex(seed or 0))
                if pc=='c0cbba':seed=snes_step(seed)[0];native_calls+=1
            if pc=='c07979':clears.append(dict(field=int(row['field']),seed=actual,level=int(row['level'],16),descriptor=int(row['descriptor'],16),x=int(row['x'],16)))
        normal.append(dict(case=name,clears=clears));checks[name+'/native_seed_events_accounted']=True
    # Re-run the component test as a bound standalone artifact, with no player.
    test=base/'rng_scene_test.exe';cmd=[test,ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md']
    result=subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True,timeout=30)
    log=base/'component-test.log';log.write_bytes(result.stdout);checks['component_guard_saved_cpu_tests']=b'PASS 1572' in result.stdout
    component=bound(base/'component2/report.json');checks['original_clear_policy_192_cases']=component['original_instruction_cases']==192
    paths.extend([ROOT/'engine/runner/tlk_rng_scene.c',ROOT/'engine/runner/tlk_rng_scene.h',ROOT/'engine/tests/rng_scene_test.c',test,ROOT/'tools/pride_rng_audit.py'])
    report=dict(result='PARTIAL' if all(checks.values()) else 'INCOMPLETE',checks=checks,check_count=len(checks),original_md_reseed_fields=reseeds,
        original_md_rng_calls=rng_calls,original_native_rng_calls=native_calls,native_clear_milestones=normal,
        original_instruction_component_cases=192,component_guard_checks=1572,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'component-test.log':digest(log)},
        prior_no_md_normal_entry_reseed_claim_superseded=True,component_installed=False,resource_capability_enabled=False,full_first_level_fidelity_complete=False)
    (base/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'build/pride-rng-lifecycle-latest.json').write_text(json.dumps(dict(result=report['result'],check_count=len(checks),component_installed=False,
        full_first_level_fidelity_complete=False,source_sha256={(base/'audit.json').relative_to(ROOT).as_posix():digest(base/'audit.json')}),indent=2)+'\n')
    print(report['result'],len(checks),'checks;',native_calls,'native RNG calls;',reseeds,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
