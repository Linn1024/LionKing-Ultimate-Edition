"""Retain current authored-route completion evidence with all supported MD rules.

Ordinary power-on controller inputs only. A failing recording must remain an
open completion item; matching AOT/LLE failures do not prove full fidelity.
"""
import hashlib
import json
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-hitbox-completion';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    profile=out/'resources.ini';profile.write_text((ROOT/'build/pride-state-profiles/all-gameplay.ini').read_text())
    tape=ROOT/'build/pride-camera-completion-verified/md-start.polled.tape'
    head=ROOT/'engine/build-win/tlk_headless.exe';modes={};tracked={}
    for mode in ('aot','lle'):
        ram=out/(mode+'.ram');log=out/(mode+'.log')
        cmd=[head,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--frames','5822','--input-polled',tape,'--ram-log',ram]
        if mode=='lle':cmd+=['--lle']
        with log.open('wb') as f:subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
        rows=[r.split() for r in ram.read_text().splitlines()];tracked[mode]=ram.read_bytes()
        # The level word is stale in menus. This ordinary prefix finishes its
        # camera/initial scan before field1000; exclude bootstrap/title values.
        pride=[r for r in rows if int(r[6],16)==0 and int(r[0])>=1000]
        losses=[int(b[0]) for a,b in zip(pride,pride[1:]) if int(a[3],16)>int(b[3],16)]
        lives=[int(b[0]) for a,b in zip(pride,pride[1:]) if int(a[7],16)>int(b[7],16)]
        modes[mode]={'hashes':hashes(log),'final_level':int(rows[-1][6],16),
            'final_xy':[int(rows[-1][i],16) for i in (4,5)],'minimum_pride_y':min(int(r[5],16) for r in pride),
            'health_loss_frames':losses,'life_loss_frames':lives}
    same=tracked['aot']==tracked['lle'] and modes['aot']==modes['lle']
    assert same,'Current full-rule recording differs between compiled and interpreted execution'
    complete=modes['aot']['final_level']==1 and modes['aot']['minimum_pride_y']<200
    report={'result':'PASS' if complete else 'FAIL','scope':__doc__,'modes':modes,
        'tracked_rows_and_final_hashes_aot_lle_identical':True,'ordinary_controller_input_only':True,
        'headless_sha256':hashlib.sha256(head.read_bytes()).hexdigest(),
        'profile_sha256':hashlib.sha256(profile.read_bytes()).hexdigest(),'tape_sha256':hashlib.sha256(tape.read_bytes()).hexdigest(),
        'normal_first_level_completion_verified':complete,'full_first_level_fidelity_complete':False}
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('Current full-rule recording completion:',report['result'],'(both modes identical)',flush=True)


if __name__=='__main__':main()
