"""Verify the independent streaming top margin on ordinary controller inputs.

This checks source isolation, original porcupine/contact observations and
execution parity. The later jump divergence after controller-read alignment
remains a visible limit; extra SNES lag fields do not imply changed gameplay.
"""
import csv
import hashlib
import json
import struct
import subprocess
import sys
from audit_scenes import ROOT


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-streaming-verification';out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    results={}
    for name,mode,source,frames in [('native','aot','snes',1600),('aot','aot','md',5500),('lle','lle','md',5500)]:
        folder=out/name
        cmd=[sys.executable,ROOT/'tools/pride_md_controller_route.py','--audit','--ceiling-rows','md',
             '--ceiling-clearance','md','--streaming-top',source,'--out',folder,'--frames',frames,
             '--dump-fields','1029,1030,1031,1404,1405,1406,1559,1560,1630,1631']
        if mode=='lle':cmd+=['--lle']
        with (out/(name+'-capture.log')).open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        results[name]=json.loads((folder/'early-audit.json').read_text())
        assert results[name]['headless_sha256']==digest(ROOT/'engine/build-win/tlk_headless.exe')
        assert results[name]['matched_initial_integer_position_fields']==(466 if source=='snes' else 620)
        assert results[name]['matched_initial_nonlag_integer_position_updates']==(466 if source=='snes' else 686)
        trace=folder/'streaming-top.csv'
        rows=list(csv.DictReader(trace.open())) if trace.exists() else []
        assert bool(rows)==(source=='md')
        for row in rows:assert int(row['selected_top'])==max(0,int(row['native_top'])-12)
    a=out/'aot';b=out/'lle'
    for name in ('native-probe.ram','frame-fnv.log','streaming-top.csv'):
        assert (a/name).read_bytes()==(b/name).read_bytes(),name
    for field in (1029,1030,1031,1404,1405,1406,1559,1560,1630,1631):
        name=f'hl_wram_{field}.bin';assert (a/name).read_bytes()==(b/name).read_bytes(),name
    def porcupines(folder,field):
        ram=(folder/f'hl_wram_{field}.bin').read_bytes();found=[]
        for actor in range(0xb313,0xc213,128):
            w=struct.unpack_from('<64H',ram,actor)
            if w[34]==11 and w[24]:found.append({'actor':actor,'xy':list(w[4:6]),'state':w[24]|w[25]<<16})
        return found
    assert not porcupines(out/'native',1030)
    assert any(r['xy']==[465,938] for r in porcupines(a,1030))
    assert any(r['xy']==[444,939] for r in porcupines(a,1405))
    report={'result':'PASS','scope':__doc__,'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
            'player_sha256':digest(ROOT/'dist/LionKing.exe'),'source_comparisons':results,
            'original_first_activation_and_contact_positions_observed':True,
            'all_5500_tracked_and_full_wram_vram_hash_fields_equal':True,'sampled_full_wram_equal':True,
            'first_level_fidelity_complete':False,'next_gap':results['aot']['first_nonlag_gap'],
            'capture_sha256':{name:digest(out/name/'early-audit.json') for name in results}}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Streaming margin: independent source, original porcupine positions,5500-field mode parity PASS;686 updates align before later jump gap',flush=True)


if __name__=='__main__':main()
