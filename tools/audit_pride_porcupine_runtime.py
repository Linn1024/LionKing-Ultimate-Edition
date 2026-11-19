"""Bind attack implementation, original evidence, failed attempts and live checks."""
import json
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-porcupine-runtime-bindings';out.mkdir();checks={}
    names=['pride-porcupine-attack2','md-porcupine-attack','pride-porcupine-attack-evidence',
           'pride-porcupine-component','pride-porcupine-runtime-guards']
    paths=[ROOT/'build'/name/'report.json' for name in names]
    reports=[bound(p) for p in paths]
    for name,r,count in zip(names,reports,[1416,5,10,708,51]):
        size=len(r['checks']) if isinstance(r['checks'],dict) else r['checks']
        checks[name+'_passes']=r['result']=='PASS' and size==count
    base=ROOT/'build/pride-porcupine38'
    for name,count in [('runtime-verification',58),('attack-ui',13)]:
        path=base/name/'report.json';r=bound(path);paths.append(path)
        checks[name+'_passes']=r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values())
    builds={}
    for number in (36,37,38):
        folder=ROOT/f'build/pride-porcupine{number}';path=folder/'build-report.json';r=bound(path);paths.append(path);builds[number]=r
        checks[f'{number}_binary']=digest(folder/'player.exe')==r['binary_sha256']
        checks[f'{number}_321_inputs']=len(r['link_inputs_sha256'])==321 and all(digest(ROOT/p)==sha for p,sha in r['link_inputs_sha256'].items())
    for left,right,label in [(36,37,'guard_only'),(37,38,'capacity_only')]:
        a=builds[left]['link_inputs_sha256'];b=builds[right]['link_inputs_sha256']
        checks[label]=len(set(a)-set(b))==len(set(b)-set(a))==1 and all(a[p]==b[p] for p in set(a)&set(b))
    gen=ROOT/'build/pride-porcupine-hooks';old=ROOT/'build/pride-pickup-flight-hooks'
    path=gen/'generation-report.json';r=bound(path);paths.append(path)
    checks['generated_sources_bound']=all(digest(gen/p)==sha for p,sha in r['generated_sha256'].items())
    checks['18_hook_units']=len(r['instrumented_units'])==18
    checks['only_new_c1_unit']=set(r['instrumented_units'])-set(json.loads((old/'generation-report.json').read_text())['instrumented_units'])=={'bankc1_part1b_v2.c'}
    checks['existing17_units_identical']=all(digest(p)==digest(old/'hooks'/p.name) for p in (gen/'hooks').glob('bank*.c') if p.name!='bankc1_part1b_v2.c')
    text=(gen/'hooks/bankc1_part1b_v2.c').read_text()
    points=[0xc15c64,0xc15d00,0xc15c8f,0xc15d14,0xc15cb2,0xc15c78,0xc15d19,0xc15ca6]
    checks['all_eight_actual_boundaries']=all(f'PrideSceneCompiledPreOpcode(cpu,0x{p:06X}u)' in text for p in points)
    catalog=(ROOT/'build/pride-porcupine36/game/tlk_resources.c').read_text()
    rows=re.findall(r'^\s*\{"([^"]+)", "[^"]*", (-?\d+),',catalog,re.M)
    node=next(i for i,r in enumerate(rows) if r[0]=='gameplay.levels.pride_lands.porcupine_attack')
    checks['append_only_node124_parent34']=node==124 and int(rows[node][1])==34 and rows[34][0]=='gameplay.levels.pride_lands'
    path=ROOT/'build/pride-porcupine36/md-aot/report.json';failed=bound(path);paths.append(path)
    checks['failed_guard_retained']=failed['result']=='FAIL' and failed['checks']['exit'] and not failed['observations']['boundaries']
    for name in ('complete-wide','complete-wide2'):
        path=ROOT/'build/pride-porcupine37'/name/'report.json';failed=bound(path);paths.append(path)
        checks[name+'_failure_retained']=failed['result']=='FAIL' and not failed['checks']['exit']
    gdb=ROOT/'build/pride-porcupine-hook-capacity/gdb.log';paths.append(gdb)
    checks['actual_exhaustion_observed']='$1 = 192' in gdb.read_text() and 'scene_hook' in gdb.read_text()
    source=ROOT/'build/pride-hook-capacity-runtime/interp_bridge.c'
    previous=ROOT/'build/pride-final-standalone/native-engine/tlk_pride_final_player_core-sources/runtime/interp_bridge.c'
    checks['bridge_only_capacity_delta']=source.read_bytes().replace(b'kInterpPreOpcodeHookSlots = 512',b'kInterpPreOpcodeHookSlots = 192')==previous.read_bytes()
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    for label,name,sha in [('helper','dist/PrepareFinalAssets.exe','1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'),
        ('public','build/pride-cold-boot2/player.exe','dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'),
        ('launcher','Play Standalone Preview.cmd','c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87')]:checks[label+'_unchanged']=digest(ROOT/name)==sha
    paths += [Path(__file__),source,ROOT/'build/pride-porcupine-hook-capacity/partial-wav-recovery.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
