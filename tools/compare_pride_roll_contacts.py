"""Retain real longer-chase differences rather than extending the short-roll claim."""
import hashlib
import json
import struct
from audit_scenes import ROOT
from compare_pride_roll_originals import compare


def main():
    out=ROOT/'build/pride-roll-contacts'
    reference=out/'md.json';source=ROOT/'build/pride-roll-grid-fixed/snes.json'
    md=json.loads(reference.read_text());native=json.loads(source.read_text())
    assert md['fresh_md_input_boot'] and native['ordinary_native_input_boot']
    assert md['settle_frames']==native['settle_frames']==256 and native['md_camera_selected'] and native['md_start_selected']
    report=compare(native['cases'],md['cases'],False)
    assert report['total_fields_per_version']==1238
    first={k:v['first_differences'][0]['index'] for k,v in report['cases'].items()}
    assert first=={'long-roll-chase':119,'repeated-roll-chase':133,'chase-and-return':119}
    # The native queue entry is still pending. Do not infer an active actor
    # merely from an old slot's retained callback/pose.
    ram=(source.parent/'long-roll-chase/snes/hl_wram_2457.bin').read_bytes()
    w=lambda at:struct.unpack_from('<H',ram,at)[0]
    node=w(0xe4c1+22*2);assert node and w(node+2)==14 and w(node+4)==156
    initial=json.loads((ROOT/'build/pride-spawn-initial/compare.json').read_text())
    assert initial['result']=='DIFFERENCE' and not initial['initialization_order_equivalent']
    a=native['cases']['long-roll-chase'][118];b=md['cases']['long-roll-chase'][118]
    originals=[s for s in b['raw_slots'] if s['state']==0x19c004 and s['words'][4:6]==[454,1261] and s['words'][34]==14]
    assert len(originals)==1
    assert not any(s['state']==0xc160d5 and s['words'][5]>=1200 and s['words'][4]<=480 and s['words'][34] for s in a['raw_slots'])
    report.update(result='PARTIAL',scope=__doc__,first_motion_difference_indices=first,
                  initial_native_ground_marker_still_queued={'id':14,'x':352,'y':1248},
                  initialization_order_evidence=initial,
                  raw_slot_observations_are_not_active_list_proof=True,
                  all_state_pair_semantics_mapped=False,
                  original_md_ground_lizard_before_contact={'index':118,'x':454,'y':1261,'marker_id_field':14},
                  actual_contact_windows={'port':str(source.parent/'contact119.png'),'md':str(out/'long-roll-chase/md-119.png')},
                  source_sha256={'native':hashlib.sha256(source.read_bytes()).hexdigest(),'md':hashlib.sha256(reference.read_bytes()).hexdigest()},
                  cause_of_all_contact_differences_proven=False,full_rolling_or_enemy_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Three longer-chase gaps retained with ordinary-boot, original lifecycle and pending-queue evidence; PARTIAL',flush=True)


if __name__=='__main__':main()
