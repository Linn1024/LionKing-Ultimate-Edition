"""Preserve the current controller-only Pride completion-route candidate.

The route remains incomplete. These are ordinary input edits to the locally
derived MD recording, with no practice menu, actor/world edits or loaded state.
The saved authoring checkpoint is observational, never loaded during this run.
"""
import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
from audit_scenes import ROOT
from verify_windows import hashes


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',action='store_true')
    parser.add_argument('--frames',type=int,default=3000)
    args=parser.parse_args()
    out=ROOT/'build/pride-route-candidate';out.mkdir(exist_ok=True)
    subprocess.run([sys.executable,str(ROOT/'tools/pride_md_controller_route.py'),'--out',str(out/'source')],cwd=ROOT,check=True)
    original=out/'source/derived.polled.tape';raw=original.read_bytes()
    values=list(struct.unpack('<'+'H'*(len(raw)//2),raw))
    assert values[1302:1306]==[0x8300,0x8300,0x8200,0x8200]
    values[1302:1306]=[0x8200]*8
    for i in range(1310,1334):values[i]=(values[i]&~0x100)|0x200
    for i in range(1475,1523):values[i]=0x8200 if i<1487 else 0x200
    tape=out/'candidate.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(values),*values))
    profile=out/'resources.ini'
    profile.write_bytes((ROOT/'build/pride-state-profiles/all-gameplay.ini').read_bytes())
    recipe={'scope':__doc__,'original_controller_source':json.loads((out/'source/provenance.json').read_text()),
            'base_tape_sha256':digest(original),'candidate_tape_sha256':digest(tape),'profile_sha256':digest(profile),
            'edits':[{'at_poll_index':1302,'replace_polls':4,'left_and_jump_polls':8},
                     {'at_poll_index':1310,'force_left_polls':24,'preserve_other_buttons':True},
                     {'at_poll_index':1475,'left_and_jump_polls':12,'then_left_only_polls':36}],
            'actor_or_world_edits':False,'loaded_states':False,'full_level_completion_proven':False}
    (out/'recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
    if not args.capture:return
    (out/'report.json').write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    host=ROOT/'engine/build-win/tlk_headless.exe';modes={}
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir(exist_ok=True)
        env=os.environ.copy();env.update(TLK_FRAME_LOG=str(folder/'frame-fnv.log'),
            TLK_WRAM_DUMP='1747,1974',TLK_WRAM_DIR=str(folder))
        cmd=[host,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--frames',args.frames,'--input-polled',tape,
             '--ram-log',folder/'game.ram','--save-at','1974',folder/'authoring.state']
        if mode=='lle':cmd+=['--lle']
        with (folder/'game.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        modes[mode]=hashes(folder/'game.log')
    assert len(modes['aot'])==2 and modes['aot']==modes['lle']
    for name in ('game.ram','frame-fnv.log','hl_wram_1747.bin','hl_wram_1974.bin'):
        assert (out/'aot'/name).read_bytes()==(out/'lle'/name).read_bytes(),name
    rows=[r.split() for r in (out/'aot/game.ram').read_text().splitlines()]
    complete=any(int(r[0])>1000 and int(r[6],16)==1 for r in rows)
    active=[r for r in rows if int(r[0])>1600 and int(r[6],16)==0]
    best=min(active,key=lambda r:int(r[5],16))
    report={'result':'PASS' if complete else 'PARTIAL','scope':__doc__,'headless_sha256':digest(host),
            'recipe_sha256':digest(out/'recipe.json'),'candidate_sha256':digest(tape),'frames':args.frames,
            'execution_modes_equal':True,'all_tracked_and_full_wram_vram_hash_fields_equal':True,
            'highest_progress':{'frame':int(best[0]),'xy':[int(best[i],16) for i in (4,5)]},
            'first_level_completed':complete,'full_first_level_fidelity_proven':False,
            'next_work':'Refine ordinary controls after the upper-left approach; final full-mixture320/256 completion remains required.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Controller candidate',report['result'],'highest progress',report['highest_progress'],'AOT/LLE parity PASS',flush=True)


if __name__=='__main__':main()
