"""Bind prepared bank5 evidence without claiming a completed playback adapter."""
import json
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def main():
    out=ROOT/'build/pride-title-bank-bindings';out.mkdir();checks={};reports={}
    names=['pride-title-audio-observer/report.json','pride-title-bank-installed/verification/report.json',
           'pride-title-bank-installed/setup-verification/report.json','pride-title-bank-installed/window/report.json',
           'pride-title-native15/build-report.json','pride-title-native15/verification/report.json',
           'pride-title-native15/contexts/report.json','pride-title-native-bindings/report.json']
    for name in names:reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    for name,count,result in [(names[0],8,'NEUTRAL'),(names[1],140,'PASS'),(names[2],21,'PASS'),(names[3],8,'PASS')]:
        r=reports[name];checks[name+'_checks']=r['result']==result and len(r['checks'])==count and all(r['checks'].values())
    observer=reports[names[0]];observer_dir=ROOT/'build/pride-title-audio-observer'
    checks['observer_binary']=digest(observer_dir/'player.exe')==observer['binary_sha256']
    checks['observer315_inputs']=len(observer['link_inputs_sha256'])==315 and all(digest(ROOT/p)==sha for p,sha in observer['link_inputs_sha256'].items())
    build=reports[names[4]]
    checks['private15_unchanged']=digest(ROOT/'build/pride-title-native15/player.exe')==build['binary_sha256']=='4e78d43a1af912271ac596a09d04faa8469e5ce6df1b9e0429ede375c6922e7f'
    checks['private15_315_inputs']=len(build['link_inputs_sha256'])==315 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    graph=ROOT/'build/pride-title-bank-installed/cmake'
    compdb=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=graph))
    entries=[r for r in compdb if r.get('file','').endswith('.c')]
    checks['fresh_helper_ten_objects']=len(entries)==10 and all((graph/r['output']).is_file() for r in entries)
    helper=graph/'tlk_prepare_final_assets.exe'
    checks['published_helper_matches_graph']=digest(helper)==digest(ROOT/'dist/PrepareFinalAssets.exe')=='1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['old_helper_archived']=digest(ROOT/'build/pride-title-bank-baseline/dist/PrepareFinalAssets.exe')=='29cd5b80913a6011ec3828f5a2e90cf686dfaf79da8b94c324cf8faf41b8c693'
    data=ROOT/'build/pride-title-bank-installed/setup-verification/Game data & title bank';manifest=data/'install.json';info=json.loads(manifest.read_text())
    checks['installed_program']=digest(data/info['title_bank_assets']['file'])==info['title_bank_assets']['sha256']=='c82576ab79d0cf52f0911c117e77e8ef0fbe34b58e5b0cc737da41bdf99292dc'
    checks['native_package_unchanged']=digest(data/info['native_final_assets']['file'])=='74364047aecdcb16cd10bead0bcf8538b845e5881f7bb54920c3a03fd7ef80ce'
    checks['menu_package_unchanged']=digest(data/info['menu_assets']['file'])=='f1e4e1f4fed4f19642b545e402c359d3fa6d1b457d2205f2470cbea1fc0bd075'
    checks['remaining_driver_delta_reported']=all(r['unmodeled_aram_changed_bytes']==249 for r in reports[names[1]]['observations'].values())
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['framework_submodules_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine',text=True).strip()
    paths=[Path(__file__),manifest,helper,ROOT/'dist/PrepareFinalAssets.exe',ROOT/'scripts/Setup.ps1',*[ROOT/'build'/n for n in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                scope='Prepared bank5 program and neutral audio evidence; playback still private15 with65/66-field title gaps',
                helper_compile_commands=entries,
                helper_source_sha256={(graph/r['file']).resolve().relative_to(ROOT).as_posix():digest(graph/r['file']) for r in entries},
                helper_object_sha256={(graph/r['output']).resolve().relative_to(ROOT).as_posix():digest(graph/r['output']) for r in entries},
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
