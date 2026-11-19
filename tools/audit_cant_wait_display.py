"""Observe second-level native end-of-field CGRAM during ordinary controller replay.

The explicit research host wraps the unchanged headless frame call. This proves
displayed native palette timing and captures inputs; it does not infer an MD
software fade clock or enable unfinished scenery. All captures stay in build/.
"""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT, read_rom
from verify_windows import hashes, pixels


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/cant-wait-display';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    player_hash=digest(ROOT/'dist/LionKing.exe');head_hash=digest(ROOT/'engine/build-win/tlk_headless.exe')
    baseline=ROOT/'build/cant-wait-native'
    audit=json.loads((baseline/'report.json').read_text())
    assert audit['headless_sha256']==head_hash
    names=('frame','level','descriptor','camera_x','camera_y','wrap_x','ride_active','transition_started',
           'dma_source','dma_bytes','dma_index','dma_pending','checkpoint_present','checkpoint_x','checkpoint_y',
           'player_x','player_y','paused','brightness','forced_blank')
    record=struct.Struct('<276I')
    palette0=(0,)+struct.unpack_from('<255H',rom,0x50b7c)
    palette1=struct.unpack_from('<256H',rom,0x601b5)
    results={};all_rows=[]
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir(exist_ok=True)
        raw_path=folder/'fields.bin';env=os.environ.copy();env['TLK_CANT_WAIT_CAPTURE']=str(raw_path)
        command=[ROOT/'engine/build-win/tlk_cant_wait_capture.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--resource-profile',baseline/'native.ini','--input-polled',ROOT/'engine/tapes/allbugsF.read.tape',
            '--frames','13500','--ram-log',folder/'route.ram']
        if mode=='lle':command+=['--lle']
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        assert hashes(folder/'run.log')==hashes(baseline/mode/'run.log')
        assert (folder/'route.ram').read_bytes()==(baseline/mode/'route.ram').read_bytes(),'Observer changed guest route'
        raw=raw_path.read_bytes();assert raw[:8]==b'CWNAT001' and (len(raw)-8)%record.size==0
        rows=[];changes=[];last=None
        for values in record.iter_unpack(raw[8:]):
            row=dict(zip(names,values[:20]));palette=values[20:]
            assert row['level']==1 and row['descriptor']==0x3b9 and all(c<=0x7fff for c in palette)
            row['palette_sha256']=hashlib.sha256(struct.pack('<256H',*palette)).hexdigest()
            row['initial_palette_matches']=sum(a==b for a,b in zip(palette,palette0))
            row['alternate_palette_matches']=sum(a==b for a,b in zip(palette,palette1))
            key=(row['transition_started'],row['dma_source'],row['dma_bytes'],row['dma_index'],row['dma_pending'],
                 row['palette_sha256'],row['brightness'],row['forced_blank'])
            if key!=last:changes.append(row)
            last=key;rows.append(row)
        assert rows and len(rows)>7000
        all_rows.append(rows)
        (folder/'fields.json').write_text(json.dumps(rows,indent=2)+'\n')
        (folder/'changes.json').write_text(json.dumps(changes,indent=2)+'\n')
        results[mode]={'fields':len(rows),'field_range':[rows[0]['frame'],rows[-1]['frame']],
                      'hashes':hashes(folder/'run.log'),'capture_sha256':digest(raw_path),
                      'tracked_ram_sha256':digest(folder/'route.ram'),'changes':len(changes)}
        print(mode,len(rows),'ordinary native displayed palette fields; observer leaves guest route unchanged PASS',flush=True)
    assert all_rows[0]==all_rows[1] and results['aot']==results['lle'],'Observed native fields differ by execution mode'
    assert digest(ROOT/'dist/LionKing.exe')==player_hash and digest(ROOT/'engine/build-win/tlk_headless.exe')==head_hash
    rows=all_rows[0]
    requested=next(r for r in rows if r['transition_started'])
    displayed=next(r for r in rows if r['alternate_palette_matches']==256)
    assert requested['frame']==4910 and requested['dma_source']==0xc601b5
    assert requested['dma_bytes']==512 and requested['dma_index']==0 and requested['dma_pending']==1
    assert requested['initial_palette_matches']==256
    assert displayed['frame']==requested['frame']+1 and displayed['dma_pending']==0
    assert all(r['alternate_palette_matches']==256 for r in rows if r['frame']>=displayed['frame'])
    # The end-of-field PPU state is not a complete scanline oracle. Check the
    # actual Windows presenter at the request and transfer boundaries too.
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    pictures=[]
    for row,palette in ((requested,palette0),(displayed,palette1)):
        folder=out/('picture-'+str(row['frame']));folder.mkdir(exist_ok=True)
        command=[ROOT/'dist/LionKing.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--resource-profile',baseline/'native.ini','--input-polled',ROOT/'engine/tapes/allbugsF.read.tape',
            '--frames',str(row['frame']),'--config',config,'--no-pace','--no-audio','--no-record',
            '--dump-window',folder/'window.png']
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str,command)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        width,height,image=pixels(folder/'window.png');assert (width,height)==(512,448)
        brightness=row['brightness']
        def color(word):return tuple(((((word>>s)&31)<<3)|(((word>>s)&31)>>2))*brightness//15 for s in (0,5,10))
        expected={color(c) for c in palette}
        actual=set(image)
        assert len(actual)>20 and actual<=expected,('Unexpected displayed colors',row['frame'],actual-expected)
        other={color(c) for c in (palette1 if row is requested else palette0)}
        unique=actual-other;assert len(unique)>5,('Palette source is visually ambiguous',row['frame'])
        pictures.append({'frame':row['frame'],'brightness':brightness,'colors':len(actual),
                         'colors_unique_to_expected_source':len(unique),'window_sha256':digest(folder/'window.png')})
        print(row['frame'],'actual Windows palette/brightness matches observed source PASS',flush=True)
    result={'result':'NATIVE_DISPLAY_CAPTURED_MD_MAPPING_OPEN','scope':__doc__,'runs':results,
            'first_transition_started':requested,'first_full_alternate_palette':displayed,
            'request_to_cgram_fields':1,'actual_windows_palette_boundaries':pictures,
            'production_hosts_unchanged':True,'mixed_background_enabled':False,
            'player_sha256':player_hash,'headless_sha256':head_hash,
            'research_host_sha256':digest(ROOT/'engine/build-win/tlk_cant_wait_capture.exe'),
            'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
                Path(__file__),ROOT/'tools/cant_wait_native_capture.c',ROOT/'engine/runner/headless_main.c',
                ROOT/'engine/CMakeLists.txt',baseline/'report.json',ROOT/'engine/tapes/allbugsF.read.tape')},
            'remaining':['Map native displayed transition to independently selected MD fade state',
                         'Latch native raster camera and wrap into the displayed background phase',
                         'Verify mixed occlusion, transitions, source switches and moving saves']}
    report.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
