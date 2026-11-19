"""Bind maintained title readiness, code generation, cold tests and source policy."""
import json
from pathlib import Path
import re
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-title-ready-runtime-bindings';out.mkdir();checks={};reports={}
    names=['pride-title-ready-hooks/generation-report.json','pride-title-upload-hooks3/generation-report.json',
           'pride-title-ready18/build-report.json','pride-title-ready18/verification/report.json',
           'pride-title-ready18/contexts/report.json','pride-title-ready18/continue-regressions/report.json',
           'pride-title-ready-state/report.json','pride-title-ready-state2/report.json',
           'pride-title-readiness-bindings/report.json','pride-title-ready18/mixtures/report.json',
           'pride-title-ready18/device/report.json']
    for name in names:reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    gen=ROOT/'build/pride-title-ready-hooks';generation=reports[names[0]]
    checks['all_generated_hashes']=all(digest(gen/p)==sha for p,sha in generation['generated_sha256'].items())
    checks['configured_program_contract_unchanged']=generation['program_contract_sha256']==reports[names[1]]['program_contract_sha256']
    checks['sixteen_units']=len(generation['instrumented_units'])==16
    text=(gen/'hooks/bankc4_part1c_v2.c').read_text()
    checks['generated_hook_and_resume']='case 0x00C465C0u: goto PRIDE_PC_C465C0_M0X0' in text and 'PrideSceneCompiledPreOpcode(cpu,0xC463FCu)' in text
    old=ROOT/'build/pride-title-upload-hooks3'
    changed=[p.name for p in sorted((gen/'hooks').glob('bank*.c')) if digest(p)!=digest(old/'hooks'/p.name)]
    checks['one_changed_c4_unit']=changed==['bankc4_part1c_v2.c']
    base=ROOT/'build/pride-title-ready18';build=reports[names[2]]
    checks['current_binary']=digest(base/'player.exe')==build['binary_sha256']
    checks['all_316_link_inputs']=len(build['link_inputs_sha256'])==316 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    for name,count in [(names[3],260),(names[4],330),(names[5],171),(names[7],42),(names[9],50),(names[10],7)]:
        report=reports[name];checks[name+'_passes']=report['result']=='PASS' and len(report['checks'])==count and all(report['checks'].values())
    checks['retained_state_test_assumption_failure']=reports[names[6]]['result']=='FAIL' and [k for k,v in reports[names[6]]['checks'].items() if not v]==['inconsistent-fade_rejects','inconsistent-fade_preserves_state']
    for width in (256,320):
        normal=(base/f'verification/{width}-menu515/run.log').read_text()
        lle=(base/f'verification/{width}-menu515-lle/run.log').read_text()
        calls=lambda s:int(re.search(r'pride_compiled_hook_calls=(\d+)',s)[1])
        checks[f'{width}_compiled_hooks_exercised']=calls(normal)>0 and calls(lle)==0
    checks['component_binary']=digest(ROOT/'build/pride-title-ready-state2/state.dll')==reports[names[7]]['binary_sha256']
    checks['helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')=='1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['private16_unchanged']=digest(ROOT/'build/pride-title-upload16/player.exe')=='734f7b63e67a9521ee0c052d5819b274432a8a34ef92851e4049e002f100530d'
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['framework_submodules_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths=[Path(__file__),*[ROOT/'build'/n for n in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
