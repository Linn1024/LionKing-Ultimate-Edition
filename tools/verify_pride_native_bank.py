"""Verify the reusable prepared native bank inside ordinary interpreted reloads.

This is an isolated integration target. It does not expose death gameplay or
modify distributed hosts. Source-bank bytes, live DSP/PCM and clocks are
verified separately from full death timing and actual Windows presentation.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--sources',nargs='+',choices=('native','both'),default=['native','both'])
    ap.add_argument('--reuse',action='store_true',help='Reanalyse existing exact-executable captures; do not replay')
    args=ap.parse_args();out=ROOT/'build/pride-native-bank';out.mkdir(exist_ok=True)
    report=out/'report.json'
    prior=json.loads(report.read_text()) if args.reuse else None
    if prior:
        assert prior['result']=='PASS' and prior['sources']==args.sources
        assert prior['probe_sha256']==digest(ROOT/'engine/build-win/tlk_native_bank_probe.exe')
        for name,sha in prior['source_sha256'].items():
            if name not in ('engine/CMakeLists.txt','tools/verify_pride_native_bank.py'):assert digest(ROOT/name)==sha,name
    report.write_text('{"result":"RUNNING"}\n')
    binary=ROOT/'engine/build-win/tlk_native_bank_probe.exe';binary_hash=digest(binary)
    prod={p:digest(ROOT/p) for p in ('dist/LionKing.exe','engine/build-win/tlk_headless.exe')}
    previous_path=ROOT/'build/pride-death-phases/report.json';previous=json.loads(previous_path.read_text());assert previous['result']=='PASS'
    zero=out/'neutral.polled.tape';zero.write_bytes(bytes(12000))
    results={}
    for source in args.sources:
        saved=out/(source+'-4000.state')
        runs={}
        for mode in ('control','prepared','loaded'):
            folder=out/(source+'-'+mode);folder.mkdir(exist_ok=True)
            env=os.environ.copy();env['TLK_NATIVE_BANK_PROBE']=str(folder);env['TLK_NATIVE_BANK_APPLY']=str(int(mode!='control'))
            env.pop('TLK_NATIVE_BANK_RECORD',None)
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--resource-profile',ROOT/f'build/pride-death-phases/{source}.ini','--input-polled',
                zero if mode=='loaded' else ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
                '--lle','--frames','5400','--ram-log',folder/'route.ram','--dump-png',folder/'picture.png']
            if mode=='control':cmd+=['--save-at','4000',saved]
            if mode=='loaded':
                cmd+=['--load',saved];env['TLK_NATIVE_BANK_RECORD']=str(out/(source+'-control')/'bank.record')
            if args.reuse:
                old=prior['runs'][source][mode]
                for key,file in (('events_sha256','events.csv'),('tracked_ram_sha256','route.ram'),('log_sha256','run.log'),('picture_sha256','picture.png')):
                    assert old[key]==digest(folder/file),(source,mode,file)
                for name,sha in old['files_sha256'].items():assert digest(folder/name)==sha,(source,mode,name)
            else:
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            events=list(csv.DictReader((folder/'events.csv').open()));points=[r for r in events if r['event']=='point']
            entry=next(int(r['field']) for r in points if r['pc']=='c089b7')
            bank_start=next(int(r['field']) for r in points if r['pc']=='c082a5')
            bank_end=next(int(r['field']) for r in points if r['pc']=='c082bb')
            normal=next(int(r['field']) for r in points if r['pc']=='c32b24')
            applied=[r for r in events if r['event']=='apply']
            if mode=='control':
                assert not applied and hashes(folder/'run.log')==previous['runs'][source]['guest']
                assert digest(folder/'route.ram')==previous['runs'][source]['tracked_sha256']
                assert bank_end-bank_start==64 and normal-entry==551
            else:
                assert len(applied)==1 and applied[0]['value1']=='1'
                assert bank_start==bank_end and normal-entry==487
            runs[mode]={'guest':hashes(folder/'run.log'),'normal_age':normal-entry,'bank_fields':bank_end-bank_start,
                'live_dsp_and_queued_pcm_preserved':bool(applied),'events_sha256':digest(folder/'events.csv'),
                'tracked_ram_sha256':digest(folder/'route.ram'),'log_sha256':digest(folder/'run.log'),
                'files_sha256':{p.name:digest(p) for p in sorted(folder.glob('*.bin'))},'picture_sha256':digest(folder/'picture.png')}
            print(source,mode,'original/control bank bytes, clock/DSP guard and normal entry',normal-entry,'PASS',flush=True)
        a=out/(source+'-control');b=out/(source+'-prepared');c=out/(source+'-loaded')
        for label in ('before-wram.bin','before-apu.bin'):
            assert (a/label).read_bytes()==(b/label).read_bytes()==(c/label).read_bytes(),(source,label)
        for label in ('after-apu.bin','after-wram.bin','normal-apu.bin','normal-wram.bin'):
            assert (b/label).read_bytes()==(c/label).read_bytes(),(source,label,'New-process component continuation differs')
        assert runs['prepared']['guest']==runs['loaded']['guest']
        assert pixels(b/'picture.png')==pixels(c/'picture.png')
        raw=(a/'after-apu.bin').read_bytes();prepared=(b/'after-apu.bin').read_bytes()
        assert raw[0x2400:0xe870]==prepared[0x2400:0xe870],source
        results[source]=runs
    assert digest(binary)==binary_hash and all(digest(ROOT/p)==sha for p,sha in prod.items())
    result={'result':'PASS','scope':__doc__,'sources':args.sources,'probe_sha256':binary_hash,
        'capture_action':'reanalysed_existing_same_binary' if args.reuse else 'fresh_replay',
        'player_sha256':prod['dist/LionKing.exe'],'headless_sha256':prod['engine/build-win/tlk_headless.exe'],
        'runs':results,'original_controls_unchanged':True,'new_process_prepared_bank_continuation':True,
        'production_component_enabled':False,'production_binaries_unchanged':True,
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),
            ROOT/'tools/pride_native_bank_probe.c',ROOT/'engine/runner/tlk_native_bank.c',ROOT/'engine/runner/tlk_native_bank.h',
            ROOT/'engine/CMakeLists.txt',previous_path)}}
    report.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
