"""Verify ordinary checkpoint collection, health death and revival for both starts.

An unchanged credited All Bugs prefix (or its controller-only MD-start retiming)
reaches the checkpoint and hyena arena. All later inputs are neutral: the hyena
depletes health, one life is lost, and original loader code restores the collected
checkpoint. No practice menu, ROM/state/actor edits or invulnerability is used.
"""
import csv
import hashlib
import json
import os
import re
import struct
import subprocess
from audit_scenes import ROOT
from pride_start_route import prepare
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-checkpoint-revival';out.mkdir(parents=True,exist_ok=True)
    original=ROOT/'engine/tapes/allbugsF.read.tape'
    adapted=prepare(original,out/'md-start.polled.tape')
    headless=ROOT/'engine/build-win/tlk_headless.exe';player=ROOT/'dist/LionKing.exe'
    results={};frames=(3740,4200,4400,4500,4700,4800,4900,4944,4960,5000,5100,5200,5400)
    for source in ('snes','md'):
        folder=out/source;folder.mkdir(exist_ok=True)
        profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\n'+
            ('gameplay.levels.pride_lands.start = md\n' if source=='md' else ''))
        prefix=adapted if source=='md' else original
        base=[headless,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',profile]
        with (folder/'prepare.log').open('wb') as log:
            subprocess.run(list(map(str,base+['--frames',3740,'--input-polled',prefix])),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        used=int(re.search(r'tape_words_used=(\d+)',(folder/'prepare.log').read_text()).group(1))
        tape=folder/'revival.polled.tape';tape.write_bytes(prefix.read_bytes()[:used*2]+bytes(5000))
        modes={};observed={}
        for mode in ('aot','lle'):
            path=folder/mode;path.mkdir(exist_ok=True)
            state=path/'during-revival.state'
            env=os.environ.copy();env.update(TLK_WRAM_DUMP=','.join(map(str,frames)),TLK_WRAM_DIR=str(path),TLK_START_TRACE=str(path/'loads.csv'))
            if mode=='lle':env['TLK_WATCH']='0xb21b'
            cmd=base+['--frames',5400,'--input-polled',tape,'--save-at',4800,state,'--ram-log',path/'game.ram']
            if mode=='lle':cmd+=['--lle']
            log=path/'game.log'
            with log.open('wb') as stream:subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
            rows={}
            for frame in frames:
                ram=(path/f'hl_wram_{frame}.bin').read_bytes();w=lambda at:struct.unpack_from('<H',ram,at)[0]
                rows[frame]={'level':w(0x1ff9e),'descriptor':w(0xdf),'xy':[w(0xb21b),w(0xb21d)],
                             'lives':w(0x1ffaa),'health':w(0x2004),'checkpoint_flag':w(0x1ffa2),
                             'checkpoint_xy':[w(0x1ffa4),w(0x1ffa6)]}
            assert rows[3740]['checkpoint_xy']==[1200,112] and rows[3740]['lives']==8 and rows[3740]['health']==6
            assert any(r['health']==0 and r['lives']==8 for r in rows.values()),'No ordinary health death observed'
            restored=[f for f,r in rows.items() if r['checkpoint_flag']==1 and r['xy']==[1200,112] and r['lives']==7]
            assert restored,'Original checkpoint loader position not observed'
            assert rows[5400]=={'level':0,'descriptor':0x387,'xy':[1200,111],'lives':7,'health':6,
                                'checkpoint_flag':0,'checkpoint_xy':[1200,112]},rows[5400]
            loads=[r for r in csv.DictReader((path/'loads.csv').open()) if r['pc'] in ('c0867d','c08689')]
            expected=[65,1255] if source=='md' else [64,1248]
            assert len(loads)==2 and [int(r['selected']) for r in loads]==expected,'Checkpoint revival incorrectly reloaded level defaults'
            if mode=='lle':assert 'by pc=C08699' in log.read_text(errors='replace'),'Original checkpoint X store was not executed'
            resume=path/'resumed.log'
            with resume.open('wb') as stream:
                subprocess.run(list(map(str,base+['--load',state,'--frames',5400]+(['--lle'] if mode=='lle' else []))),cwd=ROOT,
                               stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
            assert hashes(resume)==hashes(log) and len(hashes(log))==2,'Revival save continuation differs'
            modes[mode]=hashes(log);observed[mode]=rows
        assert modes['aot']==modes['lle'] and observed['aot']==observed['lle']
        assert (folder/'aot/game.ram').read_bytes()==(folder/'lle/game.ram').read_bytes(),'Tracked revival path differs'
        for frame in frames:
            name=f'hl_wram_{frame}.bin';assert (folder/'aot'/name).read_bytes()==(folder/'lle'/name).read_bytes()
        config=folder/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
        cmd=[player,*base[1:],'--config',config,'--frames',5400,'--input-polled',tape,'--no-audio','--no-pace','--no-record',
             '--dump-window',folder/'revived.png','--dump-scene',folder/'scene.json']
        with (folder/'player.log').open('wb') as stream:subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
        scene=json.loads((folder/'scene.json').read_text());assert scene['level']==0 and scene['stage_detected']
        assert hashes(folder/'player.log')==modes['aot'],'Actual player revival differs from headless'
        results[source]={'hashes':modes['aot'],'observations':observed['aot'],'prefix_polls':used,
                         'tape_sha256':hashlib.sha256(tape.read_bytes()).hexdigest(),'original_checkpoint_store_executed':True,
                         'checkpoint_restoration_observed_fields':restored,'new_process_mid_revival_save_exact_both_modes':True,
                         'actual_player_matches_headless':True,'window':str(folder/'revived.png')}
        print(source,'ordinary health death/checkpoint revival, AOT/LLE and mid-revival saves PASS',flush=True)
    report={'result':'PASS','scope':__doc__,'runs':results,'player_sha256':hashlib.sha256(player.read_bytes()).hexdigest(),
            'headless_sha256':hashlib.sha256(headless.read_bytes()).hexdigest(),'frames':5400,
            'fall_death_gameover_and_all_checkpoint_variants_proven':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
