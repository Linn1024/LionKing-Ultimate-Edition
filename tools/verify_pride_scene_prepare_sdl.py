"""Check prepared scene-body reloads in actual Windows/PCM control and combined runs."""
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
    parser.add_argument('--reuse',action='store_true',help='Reanalyse unchanged-executable captures without replay')
    args=parser.parse_args()
    out=ROOT/'build/pride-scene-prepare-sdl';out.mkdir(exist_ok=True)
    report=out/'report.json';prior=json.loads(report.read_text()) if args.reuse else None
    if prior:
        assert prior['result']=='SCENE_PREPARATION_VERIFIED_CROSS_HOST_MIXED_AUDIO_OPEN'
        assert prior['probe_sha256']==digest(ROOT/'engine/build-win/tlk_scene_prepare_sdl.exe')
        for name,sha in prior['source_sha256'].items():
            if name not in ('engine/CMakeLists.txt','tools/verify_pride_scene_prepare_sdl.py','build/pride-scene-prepare/report.json'):
                assert digest(ROOT/name)==sha,name
    report.write_text('{"result":"RUNNING"}\n')
    binary=ROOT/'engine/build-win/tlk_scene_prepare_sdl.exe';exe_hash=digest(binary)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    prod={p:digest(ROOT/p) for p in ('dist/LionKing.exe','engine/build-win/tlk_headless.exe')}
    results={}
    for source in ('native','both'):
        for mode in (('control','combined') if source=='native' else ('control','combined','combined-repeat')):
            combined=mode!='control'
            case=source+'-'+mode;folder=out/case;folder.mkdir(exist_ok=True)
            env=os.environ.copy();env['TLK_NATIVE_BANK_PROBE']=env['TLK_SCENE_PREPARE_PROBE']=str(folder)
            env['TLK_NATIVE_BANK_APPLY']=env['TLK_SCENE_PREPARE_APPLY']=str(int(combined))
            env.pop('TLK_NATIVE_BANK_RECORD',None)
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--config',config,'--resource-profile',ROOT/f'build/pride-death-phases/{source}.ini',
                '--lle','--frames','5400','--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
                '--no-pace','--no-audio','--no-record','--wav',folder/'route.wav','--wav-seconds','100',
                '--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
            if args.reuse:
                for name,sha in prior['runs'][case]['artifacts_sha256'].items():assert digest(folder/name)==sha,(case,name)
            else:
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            points=list(csv.DictReader((folder/'events.csv').open()))
            marks={r['pc']:int(r['field']) for r in points if r['event']=='point'}
            age=marks['c32b24']-marks['c089b7'];assert age==(469 if combined else 551),case
            rows=list(csv.DictReader((folder/'decompress.csv').open()))
            applied=[r for r in rows if r['event']=='prepared'];assert len(applied)==(7 if combined else 0)
            pcm=wav_data(folder/'route.wav');assert pcm and pixels(folder/'window.png')[:2]==(512,448)
            cross_host=None;normal_differences=[]
            if not combined:
                baseline=ROOT/f'build/pride-health-death-music/{source}-lle'
                assert hashes(folder/'run.log')==hashes(baseline/'run.log') and pcm==wav_data(baseline/'route.wav'),case
            else:
                baseline=ROOT/f'build/pride-scene-prepare/{source}-combined'
                guest=hashes(folder/'run.log');headless=hashes(baseline/'run.log')
                assert guest['frame_sha256']==headless['frame_sha256'],case
                cross_host=guest['wram_sha256']==headless['wram_sha256']
                if source=='native':assert cross_host,case
                a=(baseline/'normal-wram.bin').read_bytes();b=(folder/'normal-wram.bin').read_bytes()
                normal_differences=[{'address':hex(i),'headless':x,'sdl':y} for i,(x,y) in enumerate(zip(a,b)) if x!=y]
                # This is a separate observed ownership check, not a claim of
                # cross-host full RAM equality: headless does not call the SDL
                # per-field audio publisher/mixer. Retain the mismatch in result.
                assert all(0x1f6f<=int(d['address'],16)<0x1fbf for d in normal_differences),(case,'Non-audio normal-state difference')
                assert pixels(folder/'guest.png')==pixels(baseline/'picture.png'),case
                a=(out/(source+'-control')/'normal-wram.bin').read_bytes();b=(folder/'normal-wram.bin').read_bytes()
                for p,n in ((0x10000,16000),(0x18800,0x2780),(0x1ba00,0x1d80),(0x1d780,0x880),(0x1e000,0xf00)):
                    assert a[p:p+n]==b[p:p+n],(case,p)
                if mode=='combined-repeat':
                    old=out/(source+'-combined')
                    assert hashes(folder/'run.log')==hashes(old/'run.log'),case
                    assert pcm==wav_data(old/'route.wav') and pixels(folder/'window.png')==pixels(old/'window.png'),case
            tail=array.array('h');tail.frombytes(pcm[-48000*4:]);peak=max(map(abs,tail));assert peak>0
            results[case]={'guest':hashes(folder/'run.log'),'normal_age':age,'prepared_bodies':len(applied),
                'pcm_bytes':len(pcm),'last_second_peak':peak,
                'cross_host_full_wram_matches':cross_host,'normal_headless_sdl_differences':normal_differences,
                'same_sdl_host_repeat_pcm_guest_and_window_exact':mode=='combined-repeat',
                'artifacts_sha256':{p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()}}
            print(case,'actual SDL/PCM,',len(applied),'prepared bodies, normal age',age,'peak',peak,'PASS',flush=True)
    assert digest(binary)==exe_hash and all(digest(ROOT/p)==sha for p,sha in prod.items())
    report.write_text(json.dumps({'result':'SCENE_PREPARATION_VERIFIED_CROSS_HOST_MIXED_AUDIO_OPEN','scope':__doc__,'runs':results,'probe_sha256':exe_hash,
        'capture_action':'reanalysed_existing_same_binary' if args.reuse else 'fresh_replay',
        'cross_host_full_mixed_wram_equivalence_verified':False,
        'production_sha256':prod,'production_decoder_bypass_enabled':False,'native_song_phase_equivalence_verified':False,
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),
            ROOT/'tools/pride_scene_prepare_probe.c',ROOT/'tools/pride_scene_template.h',ROOT/'tools/pride_native_bank_probe.c',
            ROOT/'engine/runner/tlk_native_bank.c',ROOT/'engine/runner/sdl_main.c',ROOT/'engine/CMakeLists.txt',
            ROOT/'build/pride-scene-prepare/report.json',ROOT/'build/pride-health-death-music/report.json')}},indent=2)+'\n')


if __name__=='__main__':main()
