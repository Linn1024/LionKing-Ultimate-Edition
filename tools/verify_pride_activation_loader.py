"""Check ordinary Pride loader checkpoints in fresh processes, in both modes.

Save before deferral, during camera seek and after the settled initial scan.
Use the exact consumed controller-read cursor. Do not edit guest state or
claim an in-scan checkpoint when this fixture has no field boundary there.
"""
import csv
import hashlib
import json
import os
import re
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-activation-loader-verified';out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'
        'gameplay.camera = md\ngameplay.levels.pride_lands.start = md\n'
        'gameplay.levels.pride_lands.activation = md\ngameplay.levels.pride_lands.lizard_reactivation = md\n'
        'gameplay.hitboxes = md\n')
    raw=(ROOT/'engine/tapes/allbugsF.read.tape').read_bytes();words=struct.unpack('<'+'H'*(len(raw)//2),raw)
    raw=raw[:words.index(0x100)*2];prefix=out/'ordinary-prefix.polled.tape';prefix.write_bytes(raw)
    host=ROOT/'engine/build-win/tlk_headless.exe';results={}
    def run(name,mode,end,tape,extra=()):
        folder=out/name;folder.mkdir(exist_ok=True);log=folder/'game.log'
        env=os.environ.copy();env['TLK_SPAWN_INIT_TRACE']=str(folder/'initial.csv')
        cmd=[host,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profile,'--frames',end,'--input-polled',tape,*extra]
        if mode=='lle':cmd+=['--lle']
        with log.open('wb') as f:subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
        trace=folder/'initial.csv';events=list(csv.DictReader(trace.open())) if trace.exists() else []
        text=log.read_text();used=int(re.search(r'tape_words_used=(\d+)',text).group(1))
        return hashes(log),used,events
    for mode in ('aot','lle'):
        baseline,_,events=run(mode+'-continuous',mode,2200,prefix)
        assert len(baseline)==2 and sum(r['event']=='activate_settled' for r in events)==1
        for frame in (928,934,939):
            name=f'{mode}-{frame}';state=out/(name+'.state')
            _,used,before=run(name+'-save',mode,frame,prefix,['--save-at',frame,state])
            remaining=out/(name+'-remaining.polled.tape');remaining.write_bytes(raw[used*2:])
            actual,_,after=run(name+'-load',mode,2200,remaining,['--load',state])
            assert actual==baseline,(mode,frame,'new-process loader continuation differs')
            assert sum(r['event']=='activate_settled' for r in before+after)==1,(mode,frame,'initial scan repeated/lost')
            data=state.read_bytes();flags=struct.unpack_from('<I',data,32)[0]
            assert flags&0x030000ff==0x030000e1
            blob=data[36:36+struct.unpack_from('<Q',data,24)[0]];residue=blob.rfind(b'RBRS')
            assert residue>=0 and struct.unpack_from('<I',blob,residue+4)[0]==7
            results[name]={'hashes':actual,'controller_polls_at_checkpoint':used,
                'resume_pc':struct.unpack_from('<I',data,16)[0],
                'cpu_stack':struct.unpack_from('<H',blob,residue+14)[0],
                'activation_before_save':any(r['event']=='activate_settled' for r in before),
                'activation_after_load':any(r['event']=='activate_settled' for r in after)}
            print('Initial activation loader:',mode,'field',frame,'exact new-process continuation PASS',flush=True)
        results[mode+'-continuous']={'hashes':baseline,'events':events}
    assert results['aot-continuous']['hashes']==results['lle-continuous']['hashes']
    report={'result':'PASS','scope':__doc__,'headless_sha256':hashlib.sha256(host.read_bytes()).hexdigest(),
        'checkpoints':results,'injected_scan_field_boundary_checkpoint_observed':False,
        'all_loader_and_revival_paths_complete':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
