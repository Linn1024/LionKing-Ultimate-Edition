"""Bind menu/navigation and subsequent transition evidence without parity claims."""
import json
import csv
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-title-options-bindings2';out.mkdir();checks={};reports={}
    names=['pride-title-ready18/options/report.json','pride-title-navigation-original/report.json',
           'pride-title-wrap-original/report.json','pride-title-wrap-original2/report.json',
           'pride-title-start-native/report.json','pride-title-start-original/report.json',
           'pride-title-start-original2/report.json','pride-title-start-native/variants/report.json',
           'pride-title-ready18/build-report.json','pride-title-ready-runtime-bindings/report.json']
    for name in names:reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    for index,count in [(0,66),(1,4),(3,6),(6,3),(7,12)]:
        r=reports[names[index]];checks[names[index]+'_passes']=r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values())
    r=reports[names[4]]
    checks['observer_neutral8']=r['result']=='NEUTRAL' and len(r['checks'])==8 and all(r['checks'].values())
    checks['observer_binary']=digest(ROOT/'build/pride-title-start-native/player.exe')==r['binary_sha256']
    checks['observer_all316_link_inputs']=len(r['link_inputs_sha256'])==316 and all(digest(ROOT/p)==sha for p,sha in r['link_inputs_sha256'].items())
    failed=reports[names[2]]
    checks['retained_wrap_assumption_failure']=failed['result']=='FAIL' and [k for k,v in failed['checks'].items() if not v]==['mixed_equal_two','one_and_two_distinct']
    a=reports[names[5]]['observations'];b=reports[names[6]]['observations']
    checks['corrected_pointer_preserves_original_pictures']=all([(x['age'],x['lit'],x['picture_sha256']) for x in a[label]['frames']]==[(x['age'],x['lit'],x['picture_sha256']) for x in b[label]['frames']] for label in a)
    checks['persistent_md_player_movement840']=reports[names[7]]['observations']['md_first_displacement']==840
    checks['native_right_movement831']=reports[names[7]]['observations']['right-normal']['first_main_displacement']==831
    checks['md_second_start600_no_picture_change']=[r['picture_sha256'] for r in b['neutral']['frames']]==[r['picture_sha256'] for r in b['second-start']['frames']]
    rows=lambda p:list(csv.DictReader(p.open()))
    checks['native_second_start600_no_picture_change']=[r['picture_fnv'] for r in rows(ROOT/'build/pride-title-start-native/320/frames.csv')]==[r['picture_fnv'] for r in rows(ROOT/'build/pride-title-start-native/variants/second-start-normal/frames.csv')]
    checks['options_full_parity_not_claimed']=reports[names[0]]['full_options_or_transition_parity_claimed'] is False
    checks['private18_unchanged']=digest(ROOT/'build/pride-title-ready18/player.exe')==reports[names[8]]['binary_sha256']
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['framework_submodules_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths=[Path(__file__),*[ROOT/'build'/p for p in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()
