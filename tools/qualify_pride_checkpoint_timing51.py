"""Bind contact-relative checkpoint timing evidence before runtime changes."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-checkpoint-timing51-qualification';out.mkdir()
    mdpath=ROOT/'build/md-checkpoint-timing51-reference/report.json'
    nativepath=ROOT/'build/pride-checkpoint-native51-reference/report.json'
    md=bound(mdpath);native=bound(nativepath)
    priorpath=ROOT/'build/pride-checkpoint-player/original-md-display/report.json'
    prior=bound(priorpath)
    assert md['result']==native['result']==prior['result']=='PASS'
    rows=json.loads((mdpath.parent/'neutral-after-contact/observations.json').read_text())
    ordinary=json.loads((mdpath.parent/'ordinary/observations.json').read_text())
    byfield={r['frame']:r for r in rows}
    cpu=md['observations']['neutral-after-contact']['cpu']
    display=md['observations']['neutral-after-contact']['display']
    contact=md['observations']['neutral-after-contact']['contact']
    snespath=ROOT/'Lion King, The (USA).sfc';mdrom=ROOT/'Lion King, The (World).md'
    snes=snespath.read_bytes();rom=mdrom.read_bytes()
    actual_native={r['frame']:r['poses'] for r in native['aot']}
    checks=dict(
        original_snes_stream=snes[0x255f3:0x25607]==bytes.fromhex('04e1fdc20418fec204e1fdc204de56c4ffff55c2'),
        original_md_stream=rom[0x978a0:0x978bc]==bytes.fromhex('050973b6050977c6140977fe050977c65a0973b65a0973b6ff0978a0'),
        md_natural_contact_coordinates=byfield[contact]['checkpoint']==[656,592],
        md_collected_stays_set=all(r['collected']==65535 for r in rows if r['frame']>=contact),
        md_first_cpu_blink_six_updates_after_contact=cpu[1]['first']==contact+6,
        md_first_display_blink_seven_fields_after_contact=display[2]['first']==contact+7,
        md_cpu_three_cycles=[g['first'] for g in cpu if g['value']==0x977fe]==[3550,3771,3992],
        md_display_three_cycles=[g['first'] for g in display if g['value']==[0x977fe]]==[3551,3772,3993],
        md_blink1_six_fields=all(g['fields']==6 for g in cpu if g['value']==0x977c6),
        md_blink2_twentyone_fields=all(g['fields']==21 for g in cpu if g['value']==0x977fe),
        md_complete_idle_runs_188_fields=[g['fields'] for g in cpu[1:-1] if g['value']==0x973b6]==[188,188],
        md_all_contact_branch_display_lags_cpu_one_field=all(
            byfield[f]['displayed'] and [m['pose'] for m in byfield[f]['displayed']]==[byfield[f-1]['pose']]
            for f in range(contact+1,4201)),
        md_original_display_control_reproduced=all(
            [r['frame'] for r in ordinary if 3500<=r['frame']<=3600 and any(m['pose']==int(pose) for m in r['displayed'])]==fields
            for pose,fields in prior['pose_matched_fields'].items()),
        md_42_prefix_ram_controls=md['observations']['ordinary']['control_snapshots']==42,
        native_base_through_contact_plus_two=all(actual_native[f]==[0xc456de] for f in (3281,3282)),
        native_first_blink_five_fields=all(actual_native[f]==[0xc2fde1] for f in range(3283,3288)),
        native_second_blink_five_fields=all(actual_native[f]==[0xc2fe18] for f in range(3288,3293)),
        native_last_blink_five_fields=all(actual_native[f]==[0xc2fde1] for f in range(3293,3298)),
        native_returns_base=all(actual_native[f]==[0xc456de] for f in [*range(3298,3305),3330]),
        native_execution_mode_captures_exact=all(native['checks'].values()))
    paths=[Path(__file__),mdpath,nativepath,priorpath,snespath,mdrom]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                native_contact_completed_field=3280,md_contact_completed_field=contact,
                native_display_holds=[5,5,5],md_display_holds=[6,21,6,188],md_cycle_fields=221,
                original_rom_or_guest_edits=False,runtime_checkpoint_timing_implemented=False,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
