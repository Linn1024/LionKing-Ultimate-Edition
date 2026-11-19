"""Exercise prepared native banks through the actual Windows presenter and PCM path.

Isolated SDL research host; this does not enable selectable death gameplay.
"""
import argparse
import array
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse',action='store_true',help='Reanalyse existing exact-executable captures; do not replay')
    args=parser.parse_args()
    out=ROOT/'build/pride-native-bank-sdl';out.mkdir(exist_ok=True)
    report=out/'report.json';prior=json.loads(report.read_text()) if args.reuse else None
    if prior:
        assert prior['result']=='PASS' and prior['probe_sha256']==digest(ROOT/'engine/build-win/tlk_native_bank_sdl.exe')
        for name,sha in prior['source_sha256'].items():
            if name not in ('engine/CMakeLists.txt','tools/verify_pride_native_bank_sdl.py'):assert digest(ROOT/name)==sha,name
    report.write_text('{"result":"RUNNING"}\n')
    binary=ROOT/'engine/build-win/tlk_native_bank_sdl.exe'
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    zero=out/'neutral.polled.tape';zero.write_bytes(bytes(12000))
    production={name:digest(ROOT/name) for name in ('dist/LionKing.exe','engine/build-win/tlk_headless.exe')}
    reference_path=ROOT/'build/pride-health-death-music/report.json'
    reference=json.loads(reference_path.read_text());assert reference['result']=='PASS'
    result={}
    for source in ('native','both'):
        state=out/(source+'-4000.state');runs={}
        for mode in ('control','prepared','loaded'):
            folder=out/(source+'-'+mode);folder.mkdir(exist_ok=True)
            env=os.environ.copy();env['TLK_NATIVE_BANK_PROBE']=str(folder)
            env['TLK_NATIVE_BANK_APPLY']=str(int(mode!='control'));env.pop('TLK_NATIVE_BANK_RECORD',None)
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--resource-profile',ROOT/f'build/pride-death-phases/{source}.ini','--config',config,
                '--lle','--frames','5400','--input-polled',zero if mode=='loaded' else ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
                '--no-pace','--no-audio','--no-record','--wav',folder/'route.wav','--wav-seconds','100',
                '--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
            if mode=='prepared':cmd+=['--save-at','4000',state]
            if mode=='loaded':
                cmd+=['--load',state];env['TLK_NATIVE_BANK_RECORD']=str(out/(source+'-prepared')/'bank.record')
            if args.reuse:
                for name,sha in prior['runs'][source][mode]['files_sha256'].items():assert digest(folder/name)==sha,(source,mode,name)
            else:
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            events=list(csv.DictReader((folder/'events.csv').open()))
            points={r['pc']:int(r['field']) for r in events if r['event']=='point'}
            age=points['c32b24']-points['c089b7'];assert age==(551 if mode=='control' else 487)
            applied=[r for r in events if r['event']=='apply'];assert len(applied)==int(mode!='control')
            if applied:assert applied[0]['value1']=='1'
            pcm=wav_data(folder/'route.wav');assert pcm
            assert pixels(folder/'window.png')[:2]==(512,448)
            if mode=='control':
                base=ROOT/f'build/pride-health-death-music/{source}-lle'
                assert hashes(folder/'run.log')==hashes(base/'run.log')
                assert pcm==wav_data(base/'route.wav'),(source,'Read-only PCM differs')
            if mode=='loaded':
                prepared=out/(source+'-prepared')
                assert pcm==wav_data(prepared/'route.wav')[-len(pcm):],(source,'Loaded PCM differs')
                assert hashes(folder/'run.log')==hashes(prepared/'run.log')
                assert pixels(folder/'window.png')==pixels(prepared/'window.png')
            # Retain measured output, without equating audible output to exact
            # original-song phase or a completed death-timing adapter.
            tail=array.array('h');tail.frombytes(pcm[-48000*4:]);peak=max(map(abs,tail))
            assert peak>0,(source,mode,'No PCM after revival')
            runs[mode]={'guest':hashes(folder/'run.log'),'normal_age':age,'audio_bytes':len(pcm),
                'last_second_peak':peak,'new_process_exact_pcm_suffix':mode=='loaded',
                'live_dsp_preserved':bool(applied),
                'files_sha256':{p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()}}
            print(source,mode,'actual Windows/PCM path, normal age',age,'last-second peak',peak,'PASS',flush=True)
        result[source]=runs
    assert all(digest(ROOT/name)==sha for name,sha in production.items())
    report.write_text(json.dumps({'result':'PASS','scope':__doc__,'runs':result,'production_component_enabled':False,
        'capture_action':'reanalysed_existing_same_binary' if args.reuse else 'fresh_replay',
        'production_sha256':production,'probe_sha256':digest(binary),'native_song_phase_equivalence_verified':False,
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),reference_path,
            ROOT/'tools/pride_native_bank_probe.c',ROOT/'engine/runner/tlk_native_bank.c',ROOT/'engine/CMakeLists.txt',
            ROOT/'engine/runner/sdl_main.c')}},indent=2)+'\n')


if __name__=='__main__':main()
