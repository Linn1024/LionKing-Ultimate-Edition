"""Verify ROM-derived initial positions through both original execution paths.

Ordinary power-on input only. Unit tests separately cover checkpoint and
unsupported-scene guards; this does not claim checkpoint revival coverage.
"""
import csv
import hashlib
import json
import os
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-start';out.mkdir(parents=True,exist_ok=True)
    results={}
    for source in ('snes','md'):
        profile=out/(source+'.ini')
        profile.write_text('schema = 1\ngame = snes\n'+
                           ('gameplay.levels.pride_lands.start = md\n' if source=='md' else ''))
        modes={}
        for mode in ('aot','lle'):
            folder=out/(source+'-'+mode);folder.mkdir(exist_ok=True)
            env=os.environ.copy();env['TLK_START_TRACE']=str(folder/'loads.csv')
            env['TLK_WRAM_DUMP']='1400';env['TLK_WRAM_DIR']=str(folder)
            cmd=[ROOT/'engine/build-win/tlk_headless.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                 '--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile,
                 '--frames',1400,'--input-polled',ROOT/'engine/tapes/allbugsF.read.tape']
            if mode=='lle':cmd+=['--lle']
            log=folder/'game.log'
            with log.open('wb') as stream:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
            assert 'Saved resource profile loaded' in log.read_text(errors='replace')
            rows=list(csv.DictReader((folder/'loads.csv').open()))
            loads=[r for r in rows if r['pc'] in ('c0867d','c08689')]
            expected=[65,1255] if source=='md' else [64,1248]
            assert len(loads)==2 and [int(r['native']) for r in loads]==[64,1248]
            assert [int(r['selected']) for r in loads]==expected
            assert all(int(r['changed'])==(source=='md') and r['checkpoint']=='0' and r['actor']=='b213' for r in loads)
            ram=(folder/'hl_wram_1400.bin').read_bytes()
            assert struct.unpack_from('<2H',ram,0x1ffa4)==tuple(expected),'original checkpoint-default stores lost selected coordinates'
            assert struct.unpack_from('<H',ram,0xdf)[0]==0x387
            modes[mode]={'hashes':hashes(log),'loads':rows,'stored_default_xy':expected}
            assert len(modes[mode]['hashes'])==2
        assert modes['aot']==modes['lle'],'compiled/interpreted initial-position paths differ'
        results[source]=modes['aot'];print(source,'original default loads and checkpoint defaults AOT/LLE PASS',flush=True)
    assert results['snes']['hashes']!=results['md']['hashes'],'new source did not change guest state'
    report={'result':'PASS','scope':__doc__,'sources':results,
            'player_sha256':hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest(),
            'headless_sha256':hashlib.sha256((ROOT/'engine/build-win/tlk_headless.exe').read_bytes()).hexdigest()}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
