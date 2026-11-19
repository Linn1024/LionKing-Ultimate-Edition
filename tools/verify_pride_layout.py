"""Verify original pickup marker relocations and both native spatial indexes."""
import csv
import json
import os
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes

def indexed_markers(ram,axis):
    word=lambda at:struct.unpack_from('<H',ram,at)[0]
    columns=word(0xd0)//2;rows=word(0xd4)
    assert (columns,rows)==(100,80),'unexpected Pride Lands index dimensions'
    root=0xe4c1+(columns*2 if axis=='rows' else 0)
    result=set()
    for coordinate in range(rows if axis=='rows' else columns):
        at=word(root+coordinate*2);seen=set()
        while at:
            assert at not in seen and at+6<=65536,'invalid native spawn index chain'
            seen.add(at);marker=word(at+2);other=word(at+4)
            assert not other&1,'unaligned spatial index coordinate'
            x,y=(other*8,coordinate*16) if axis=='rows' else (coordinate*16,other*8)
            result.add((marker,x,y));at=word(at)
    return result

def main():
    dest=ROOT/'build/pride-layout-verification';dest.mkdir(parents=True,exist_ok=True)
    results={};old={(0x12,320,496),(0x29,560,208)};new={(0x12,336,496),(0x29,560,224)}
    moves={(0x12,320,496,336,496),(0x29,560,208,560,224)}
    for name in ('snes','md-aot','md-lle'):
        folder=dest/name;folder.mkdir(exist_ok=True)
        profile=folder/'resources.ini'
        profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'+
                           ('gameplay.levels.pride_lands.pickups = md\n' if name!='snes' else ''))
        env=os.environ.copy();env['TLK_LAYOUT_TRACE']=str(folder/'moves.csv')
        env['TLK_WRAM_DUMP']='1000';env['TLK_WRAM_DIR']=str(folder)
        cmd=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
             '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
             '--frames','5000','--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),
             '--wide','320','--ram-log',str(folder/'game.ram')]
        if name=='md-lle':cmd+=['--lle']
        with (folder/'game.log').open('wb') as output:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=240)
        ram=(folder/'hl_wram_1000.bin').read_bytes()
        axes={}
        for axis in ('rows','columns'):
            markers=indexed_markers(ram,axis);expected=old if name=='snes' else new;absent=new if name=='snes' else old
            assert expected<=markers,name+' missing marker in '+axis
            assert not absent&markers,name+' retained incorrect marker in '+axis
            axes[axis]=len(markers)
        if name!='snes':
            observed={tuple(int(row[k]) for k in ('marker','native_x','native_y','md_x','md_y'))
                      for row in csv.DictReader((folder/'moves.csv').open())}
            assert observed==moves,name+' did not apply exactly the reviewed moves'
        transitions=[];prior=None
        for line in (folder/'game.ram').read_text().splitlines():
            row=line.split();level=int(row[6],16)
            if level!=prior:transitions.append({'frame':int(row[0]),'level':level});prior=level
        assert transitions[-1]['level']==1 and any(x['level']==10 for x in transitions),name+' did not complete Pride Lands and its bonus'
        results[name]={'hashes':hashes(folder/'game.log'),'indexed_markers':axes,'transitions':transitions}
        assert len(results[name]['hashes'])==2
        print(name,'both pickup indexes PASS',flush=True)
    assert results['md-aot']==results['md-lle'],'MD pickup placement AOT/LLE differs'
    assert (dest/'md-aot/game.ram').read_bytes()==(dest/'md-lle/game.ram').read_bytes(),'MD pickup tracked gameplay differs'
    (dest/'report.json').write_text(json.dumps({'result':'PASS','runs':results},indent=2)+'\n')

if __name__=='__main__':main()
