"""Bind experimental title upload protocol, retained failures and lifecycle evidence."""
import csv
import json
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def main():
    out=ROOT/'build/pride-title-upload-bindings';out.mkdir();checks={};reports={}
    names=['pride-title-audio-protocol/report.json',
           'pride-title-upload-prototype/report.json','pride-title-upload-prototype2/report.json',
           'pride-title-upload-fast2/report.json','pride-title-upload-prototype3/report.json',
           'pride-title-upload-fast3/report.json','pride-title-upload-prototype4/report.json',
           'pride-title-upload-fast4/report.json','pride-title-upload-lifecycle4/report.json',
           'pride-title-upload-prototype5/report.json','pride-title-upload-fast5/report.json',
           'pride-title-upload-lifecycle5/report.json','pride-title-upload-contexts5/report.json',
           'pride-title-bank-bindings/report.json']
    for name in names:reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    for name in ['pride-title-audio-protocol',*[f'pride-title-upload-prototype{x}' for x in ('','2','3','4','5')]]:
        report=reports[name+'/report.json'];base=ROOT/'build'/name
        checks[name+'_binary']=digest(base/'player.exe')==report['binary_sha256']
        expected=315 if name=='pride-title-audio-protocol' else 316
        checks[name+'_link_inputs']=len(report['link_inputs_sha256'])==expected and all(digest(ROOT/p)==sha for p,sha in report['link_inputs_sha256'].items())
    for name,count,result in [('pride-title-audio-protocol',8,'NEUTRAL'),('pride-title-upload-prototype5',8,'NEUTRAL'),
                              ('pride-title-upload-fast5',14,'OBSERVED'),('pride-title-upload-lifecycle5',52,'PASS'),
                              ('pride-title-upload-contexts5',56,'PASS')]:
        r=reports[name+'/report.json'];checks[name+'_all_checks']=r['result']==result and len(r['checks'])==count and all(r['checks'].values())
    checks['first_bulk_variant_observed_unused']=all(len(list(csv.reader((ROOT/f'build/pride-title-upload-prototype/{w}/upload.csv').open())))==1 for w in (256,320))
    checks['cursor_failure_retained']=reports['pride-title-upload-fast2/report.json']['result']=='FAIL'
    checks['cold_failure_retained']=reports['pride-title-upload-lifecycle4/report.json']['result']=='FAIL'
    for width in (256,320):
        fast=ROOT/f'build/pride-title-upload-fast5/{width}';control=ROOT/f'build/pride-title-upload-prototype5/{width}'
        checks[f'{width}_whole_aram_exact']=(fast/'after-aram.bin').read_bytes()==(control/'after-aram.bin').read_bytes()
        checks[f'{width}_whole_host_driver_exact']=(fast/'after-wram.bin').read_bytes()[0x1f00:0x2000]==(control/'after-wram.bin').read_bytes()[0x1f00:0x2000]
        r=reports['pride-title-upload-fast5/report.json']['observations'][str(width)]
        checks[f'{width}_two_field_upload']=r['events'][1]['age']-r['events'][0]['age']==2
        checks[f'{width}_first_title372']=r['first_title']==372 and r['remaining_fields']==2
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['private15_unchanged']=digest(ROOT/'build/pride-title-native15/player.exe')=='4e78d43a1af912271ac596a09d04faa8469e5ce6df1b9e0429ede375c6922e7f'
    checks['helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')=='1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['framework_submodules_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine',text=True).strip()
    paths=[Path(__file__),*[ROOT/'build'/n for n in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                scope='Research interpreted prototype; compiled hooks, installed-bank save identity and production integration remain open',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
