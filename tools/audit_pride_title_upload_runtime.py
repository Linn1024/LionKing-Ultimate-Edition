"""Bind compiled title upload, generated resume site, real audio and source mixtures."""
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def main():
    out=ROOT/'build/pride-title-upload-runtime-bindings2';out.mkdir();checks={};reports={}
    names=['pride-title-upload-hooks2/generation-report.json','pride-title-upload-hooks3/generation-report.json',
           'pride-title-upload16/build-report.json','pride-title-upload16/verification/report.json',
           'pride-title-upload16/verification2/report.json','pride-title-upload16/continue-regressions/report.json',
           'pride-title-upload16/contexts/report.json','pride-title-upload16/mixtures/report.json',
           'pride-title-upload16/mixtures2/report.json','pride-title-upload-native-observer/report.json',
           'pride-title-upload-modes-bindings/report.json','pride-title-bank-bindings/report.json']
    for name in names:reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    generation=ROOT/'build/pride-title-upload-hooks3';generated=reports[names[1]]
    checks['all_generated_hashes']=all(digest(generation/p)==sha for p,sha in generated['generated_sha256'].items())
    checks['sixteen_hook_units']=len(generated['instrumented_units'])==16
    contract=json.loads((ROOT/'engine/recomp/pride_program_contract.json').read_text())
    checks['configured_program_contract_unchanged']=generated['program_contract_sha256']==contract['program_manifest_sha256']
    text=(generation/'hooks/bankc2_part14_v2.c').read_text()
    checks['generated_read_and_resume_sites']='PRIDE_PC_C22036_M0X0' in text and 'PRIDE_PC_C22038_M0X0' in text
    strip=lambda s:'\n'.join(line for line in s.splitlines() if line.strip() and line.strip()!='#include "pride_scene_compiled_hooks_api.h"')
    checks['part13_only_api_include']=strip((generation/'hooks/bankc2_part13_v2.c').read_text())==strip((ROOT/'build/pride-title-fade-hooks/hooks/bankc2_part13_v2.c').read_text())
    for name,count in [('pride-title-upload16/verification2/report.json',114),('pride-title-upload16/continue-regressions/report.json',171),
                       ('pride-title-upload16/contexts/report.json',49),('pride-title-upload16/mixtures2/report.json',50)]:
        r=reports[name];checks[name+'_passes']=r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values())
    checks['retained_device_assumption_failure']=reports['pride-title-upload16/verification/report.json']['result']=='FAIL'
    checks['retained_unsupported_parent_failure']=reports['pride-title-upload16/mixtures/report.json']['result']=='FAIL'
    for folder,report_name in [('pride-title-upload16','pride-title-upload16/build-report.json'),
                              ('pride-title-upload-native-observer','pride-title-upload-native-observer/report.json')]:
        r=reports[report_name];checks[folder+'_binary']=digest(ROOT/'build'/folder/'player.exe')==r['binary_sha256']
        checks[folder+'_316_link_inputs']=len(r['link_inputs_sha256'])==316 and all(digest(ROOT/p)==sha for p,sha in r['link_inputs_sha256'].items())
    checks['observer_neutral8']=reports['pride-title-upload-native-observer/report.json']['result']=='NEUTRAL' and all(reports['pride-title-upload-native-observer/report.json']['checks'].values())
    original=ROOT/'build/pride-title-audio-observer/report.json';bound(original)
    for width in (256,320):
        a=ROOT/f'build/pride-title-upload-native-observer/{width}';b=original.parent/str(width)
        checks[f'{width}_native_whole_aram_original']=(a/'after-aram.bin').read_bytes()==(b/'after-aram.bin').read_bytes()
        checks[f'{width}_native_host_driver_original']=(a/'after-wram.bin').read_bytes()[0x1f00:0x2000]==(b/'after-wram.bin').read_bytes()[0x1f00:0x2000]
        events=[json.loads(s) for s in (a/'audio.jsonl').read_text().splitlines()]
        checks[f'{width}_native_two_field_upload']=events[1]['age']-events[0]['age']==2
    base=ROOT/'build/pride-title-upload16';cmd=[str(base/'player.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
        '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(out/'host.ini'),'--resource-profile',str(out/'unused.ini'),
        '--prepare-resources',str(out/'scenes.cache'),'--no-audio']
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_FINAL_MD_ART']='1'
    with (out/'prepare.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    checks['preparation_needs_no_runtime_packages']=r.returncode==0 and b'resource_cache=prepared' in (out/'prepare.log').read_bytes()
    checks['helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')=='1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['private15_unchanged']=digest(ROOT/'build/pride-title-native15/player.exe')=='4e78d43a1af912271ac596a09d04faa8469e5ce6df1b9e0429ede375c6922e7f'
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['framework_submodules_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine',text=True).strip()
    paths=[Path(__file__),original,*[ROOT/'build'/n for n in names],ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',ROOT/'engine/cmake/final-frontend-patches/presentation.hunks']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,preparation_command=cmd,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
