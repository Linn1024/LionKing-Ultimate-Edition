"""Verify 15 original rolling protocols with MD start and original320 camera.

The original MD reference is an ordinary-input boot. Port fixtures use the
original practice menu and idle inputs; no guest state/position edits occur.
The narrower native-camera mixture remains a separate, intentionally different
enemy activation environment. These finite protocols do not prove all rolling
or enemy behaviors.
"""
import hashlib
import json
import os
import struct
import subprocess
from audit_scenes import ROOT
from compare_pride_roll_originals import compare
from pride_movement_audit import ROLL_VARIANTS
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-roll-verified';out.mkdir(parents=True,exist_ok=True)
    reference=ROOT/'build/pride-roll-original/md.json'
    original=json.loads(reference.read_text())
    capture=ROOT/'build/pride-roll-md-camera/snes.json'
    native=json.loads(capture.read_text())
    assert original['fresh_md_input_boot'] and original['settle_frames']==native['settle_frames']==256
    assert native['md_start_selected'] and native['md_camera_selected']
    host=ROOT/'engine/build-win/tlk_headless.exe'
    assert capture.stat().st_mtime>=host.stat().st_mtime,'Recapture native interpreter protocols on current build'
    ready=capture.parent/'ready-native.state';raw=ready.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==native['ready_checkpoint_sha256']
    assert struct.unpack_from('<I',raw,12)[0]==2200
    flags=struct.unpack_from('<I',raw,32)[0]
    assert flags&63==33 and flags>>8&65535==320,'Fixture must select only MD initial position/camera320'
    profile=capture.parent/'native.ini'
    results={};aot={}
    for name,protocol in ROLL_VARIANTS.items():
        assert [r['pad'] for r in original['cases'][name]]==protocol
        folder=out/name;folder.mkdir(exist_ok=True)
        tape=folder/'input.tape';start=2456
        tape.write_bytes(struct.pack('<'+str(start+len(protocol))+'H',*([0]*start+protocol)))
        env=os.environ.copy();env.update(TLK_WRAM_DUMP=','.join(map(str,range(start+1,start+len(protocol)+1))),TLK_WRAM_DIR=str(folder))
        log=folder/'game.log'
        cmd=[host,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--load',ready,'--frames',start+len(protocol),'--input',tape]
        with log.open('wb') as stream:subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
        baseline=capture.parent/name/'snes';rows=[]
        for index,pad in enumerate(protocol):
            file=f'hl_wram_{start+index+1}.bin';ram=(folder/file).read_bytes()
            assert ram==(baseline/file).read_bytes(),(name,index,'full AOT/LLE WRAM differs')
            w=lambda at:struct.unpack_from('<H',ram,at)[0]
            assert w(0x1ff9e)==0 and w(0xdf)==0x387
            draw=w(0xb21f);assert draw<65514
            rows.append({'frame':index,'pad':pad,'x':w(0xb21b),'y':w(0xb21d),'health':w(0x2004),
                         'words':list(struct.unpack_from('<64H',ram,0xb213)),
                         'pose':int.from_bytes(ram[draw+10:draw+13],'little')&0x3fffff})
        assert hashes(log)==hashes(baseline/'game.log'),name+' final frame/WRAM hashes differ'
        assert len(hashes(log))==2
        aot[name]=rows;results[name]={'fields':len(protocol),'hashes':hashes(log),'every_full_wram_field_aot_lle_identical':True}
    comparison=compare(aot,original['cases'],False)
    assert len(comparison['cases'])==15 and all(r['result']=='MATCH' for r in comparison['cases'].values())
    assert comparison['total_fields_per_version']==2561 and comparison['paired_roll_pose_counter_fields']==475
    narrow=compare(json.loads((ROOT/'build/pride-roll-md-start/snes.json').read_text())['cases'],original['cases'],False)
    gaps=[name for name,row in narrow['cases'].items() if row['result']!='MATCH']
    assert set(gaps)=={'right-roll-held','repeated-roll'},'Re-evaluate narrow-camera control fixture'
    report={'result':'PASS','scope':__doc__,'player_sha256':hashlib.sha256((ROOT/'dist/LionKing.exe').read_bytes()).hexdigest(),
            'headless_sha256':hashlib.sha256(host.read_bytes()).hexdigest(),'cases':results,'original_comparison':comparison,
            'absolute_q16_positions_full_velocities_health_state_paths_match':True,
            'camera_source_controls_enemy_activation_environment':True,'native_camera_control_gaps':gaps,
            'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
            'native_capture_sha256':hashlib.sha256(capture.read_bytes()).hexdigest(),
            'all_rolling_and_enemy_behavior_proven':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('All15 original320 rolling protocols:2561 absolute fields,475 roll pose/counters, full AOT/LLE identity PASS',flush=True)


if __name__=='__main__':main()
