"""Bind the reviewed flight runtime, source tree, generated shard and save repair."""
import json
from pathlib import Path
import re
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-pickup-flight-runtime-bindings';out.mkdir();checks={};reports={}
    names=['pride-pickup-flight-motion2/report.json','pride-pickup-flight-motion-bindings/report.json',
           'pride-title-navigation-hooks/generation-report.json','pride-pickup-flight-hooks/generation-report.json',
           'pride-audio-prime30/build-report.json','pride-pickup-flight34/build-report.json','pride-pickup-flight35/build-report.json',
           'pride-pickup-flight34/integration/report.json','pride-pickup-flight35/save-verification/report.json',
           'pride-pickup-flight34/flight-ui/report.json','pride-pickup-flight35/flight-ui/report.json',
           'pride-pickup-flight34/flight-tree-view/report.json',
           'pride-pickup-flight31/failed-build.json','pride-pickup-flight32/failed-build.json','pride-pickup-flight33/failed-build.json']
    for name in names:reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    for index,count in [(0,2311),(1,13),(8,30),(9,13),(10,13),(11,3)]:
        r=reports[names[index]];checks[names[index]+'_passes']=r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values())
    failed=reports[names[7]]
    checks['retained_save_source_bug']=failed['result']=='FAIL' and len(failed['checks'])==49 and sum(failed['checks'].values())==48
    for index in [12,13,14]:checks[names[index]+'_aborted']=reports[names[index]]['result']=='ABORTED'
    gen=ROOT/'build/pride-pickup-flight-hooks';generation=reports[names[3]]
    checks['all_generated_hashes']=all(digest(gen/p)==sha for p,sha in generation['generated_sha256'].items())
    checks['same_program_contract']=generation['program_contract_sha256']==reports[names[2]]['program_contract_sha256']
    checks['17_instrumented_units']=len(generation['instrumented_units'])==17
    previous_gen=ROOT/'build/pride-title-navigation-hooks'
    changed=[p.name for p in (gen/'hooks').glob('bank*.c') if digest(p)!=digest(previous_gen/'hooks'/p.name)]
    checks['only_c5_generated_change']=changed==['bankc5_part1a_v2.c']
    text=(gen/'hooks/bankc5_part1a_v2.c').read_text()
    points=[0xc5531b,0xc554e7,0xc55343,0xc5550f,0xc553b4,0xc5557e,0xc5540c,0xc555c7]
    checks['eight_actual_flight_boundaries']=all(f'PrideSceneCompiledPreOpcode(cpu,0x{p:06X}u)' in text for p in points)
    for index,count in [(4,317),(5,319),(6,319)]:
        r=reports[names[index]];folder=(ROOT/'build'/names[index]).parent
        checks[folder.name+'_binary']=digest(folder/'player.exe')==r['binary_sha256']
        checks[folder.name+'_inputs']=len(r['link_inputs_sha256'])==count and all(digest(ROOT/p)==sha for p,sha in r['link_inputs_sha256'].items())
        checks[folder.name+'_md_component']=digest(folder/'genesis_plus_gx_libretro.dll')==digest(ROOT/'build/pride-audio-prime30/genesis_plus_gx_libretro.dll')
    a=reports[names[5]]['link_inputs_sha256'];b=reports[names[6]]['link_inputs_sha256']
    checks['save_repair_changes_only_backend_object']=len(set(a)-set(b))==len(set(b)-set(a))==1 and all(a[p]==b[p] for p in set(a)&set(b))
    catalog=(ROOT/'build/pride-pickup-flight34/game/tlk_resources.c').read_text()
    rows=re.findall(r'^\s*\{"([^"]+)", "[^"]*", (-?\d+),',catalog,re.M)
    node=next(i for i,r in enumerate(rows) if r[0]=='gameplay.levels.pride_lands.pickup_flight')
    checks['append_only_leaf123_parent34']=node==123 and rows[int(rows[node][1])][0]=='gameplay.levels.pride_lands' and int(rows[node][1])==34
    checks['version4_source_and_width_policy']='flags|=0x00800000u' in (ROOT/'build/pride-pickup-flight35/game/tlk_savestate.c').read_text()
    checks['helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')=='1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths=[Path(__file__),*[ROOT/'build'/name for name in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
