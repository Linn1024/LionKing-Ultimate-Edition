"""Verify independent Pride body-bound choices and original long-contact matches.

Four fresh ordinary-input fixtures select the two body-bound leaves separately.
Trace every selected operand against the ROMs, retain valid mixed-source
differences, and require all three full MD-source contact protocols to match.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
from audit_scenes import ROOT
from compare_pride_roll_originals import compare


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-hitbox-verification';out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    head=ROOT/'engine/build-win/tlk_headless.exe';player=ROOT/'dist/LionKing.exe'
    md=json.loads((ROOT/'build/pride-roll-contacts/md.json').read_text())['cases']
    snes_rom=(ROOT/'Lion King, The (USA).sfc').read_bytes();md_rom=(ROOT/'Lion King, The (World).md').read_bytes()
    mapping={int(a,16):(int(b,16),int(role)) for a,b,role in re.findall(r'\{0x([0-9a-f]+),0x([0-9a-f]+),([0-3])\}',
        (ROOT/'engine/generated/resources/pride_hitbox_map.h').read_text())}
    results={}
    for selection,mask in (('',0),('simba',0x01000000),('enemies',0x02000000),('both',0x03000000)):
        name=selection or 'native';folder=out/name;folder.mkdir(exist_ok=True)
        log=folder/'capture.log'
        command=[sys.executable,ROOT/'tools/pride_movement_audit.py','--source','snes','--ordinary-boot',
            '--md-start','--md-camera','--md-activation','--md-reactivation','--roll-contact-variants',
            '--settle-frames','256','--actor-slots','--out',folder]
        if selection:command+=['--md-body-bounds',selection]
        with log.open('wb') as f:subprocess.run(list(map(str,command)),cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=300)
        capture=json.loads((folder/'snes.json').read_text())
        assert capture['headless_sha256']==digest(head) and capture['player_sha256']==digest(player)
        flags=struct.unpack_from('<I',(folder/'ready-native.state').read_bytes(),32)[0]
        assert flags&0x03000000==mask and flags&255==225
        comparison=compare(capture['cases'],md,False)
        if selection=='both':assert all(r['result']=='MATCH' for r in comparison['cases'].values())
        trace=folder/'operands.csv';trace.unlink(missing_ok=True)
        env=os.environ.copy();env['TLK_HITBOX_TRACE']=str(trace)
        probe=[head,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',folder/'native.ini','--load',folder/'ready-native.state','--frames','2580',
            '--input',folder/'chase-and-return/snes/input.tape']
        with (folder/'probe.log').open('wb') as f:subprocess.run(list(map(str,probe)),cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=90)
        operands=list(csv.DictReader(trace.open())) if trace.exists() else []
        kinds=set()
        for row in operands:
            pose=int(row['pose'],16)&0x3fffff;component=int(row['component']);external,role=mapping[pose]
            enemy=int(row['actor'],16)!=0xb213;kinds.add('enemies' if enemy else 'simba')
            assert (role in (1,2,3))==enemy
            assert int(row['native'],16)==struct.unpack_from('<H',snes_rom,pose+12+component*2)[0]
            assert int(row['md'],16)==struct.unpack_from('>H',md_rom,external+12+component*2)[0]
        assert kinds==({'simba','enemies'} if selection=='both' else {selection} if selection else set())
        results[name]={'original_comparison':comparison,'source_flags':flags,'trace_operands':len(operands),
            'selected_categories':sorted(kinds),'capture_sha256':digest(folder/'snes.json')}
        print('Independent body bounds:',name,'ROM operands and source flags PASS',flush=True)
    report={'result':'PASS','scope':__doc__,'player_sha256':digest(player),'headless_sha256':digest(head),
        'choices':results,'full_md_contact_fields':1238,'all_enemy_and_collision_fidelity_complete':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
