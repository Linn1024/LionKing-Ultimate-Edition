"""Bind both original ledge directions, complete native lifetimes and FM94 tail."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arrival_history import bound


def main():
    out=ROOT/'build/pride-ledge-lifetimes';out.mkdir()
    native_path=ROOT/'build/native-ledge-lifetime/report.json';native=bound(native_path)
    md_path=ROOT/'build/pride-cub-contact-audio/report.json';md=bound(md_path)
    first_path=ROOT/'build/pride-ledge-grab-audio/report.json';first=bound(first_path)
    tail_path=ROOT/'build/pride-ledge-tail/report.json';tail=bound(tail_path)
    observer_path=ROOT/'build/native-ledge-audio/report.json';observer=bound(observer_path)
    assert native['result']=='ORIGINAL_LEDGE_LIFETIMES_CAPTURED'
    assert observer['observer_neutral_all_2000_picture_full_wram_fields']
    assert native['observer_neutral_all_4500_picture_full_wram_fields'] and native['native_audio_and_entry_traces_unchanged']
    assert first['result']=='ORIGINAL_FIRST_SHARED_LEDGE_SOUND_DIFFERENCE_VERIFIED'
    intervals=native['intervals'];assert len(intervals)==5
    assert all(r['consecutive_ledge_fields']>0 and not r['native_audio_in_enclosing_window'] for r in intervals)
    assert {r['expected_ledge_action'] for r in intervals}=={'c33d1f','c33f11'}
    paired=[]
    for native_field,md_field in ((1472,1874),(2347,2703),(4032,4191)):
        a=next(r for r in intervals if int(r['entry']['field'])==native_field)
        b=next(r for r in md['observations'] if r['field']==md_field)
        entry=next(r for r in md['entries'] if int(r['field'])==md_field)
        after=a['initial_post_field']
        assert (int(after['x']),int(after['y']),int(after['timer']))==(b['x'],b['y'],b['timer'])
        assert int(after['timer'])==42 and a['entry']['tag']==entry['tag']
        assert {'c33d1f':'194b94','c33f11':'194da6'}[after['action']]==b['action']
        paired.append(dict(native_entry=a['entry'],native_post=after,md_entry=entry,md_post=b,
            native_ledge_fields=a['consecutive_ledge_fields'],native_sound_calls=0))
    assert tail['result']=='PASS' and tail['original_command']==[2,94] and tail['last_field_above_one']==13
    paths=[Path(__file__),native_path,md_path,first_path,tail_path,observer_path]
    report=dict(result='ORIGINAL_BOTH_LEDGE_SOUND_DIFFERENCES_VERIFIED',paired=paired,
        all_native_contact_intervals=intervals,native_complete_lifetime_field_counts=[r['consecutive_ledge_fields'] for r in intervals],
        md_fm_command=[2,94],original_tail_last_field_above_one=13,existing_120_field_hold_sufficient=True,
        observed_native_tags=sorted({r['entry']['tag'] for r in intervals}),
        directions_both_observed=True,all_possible_contact_tags_verified=False,
        arbitrary_movement_or_timing_equivalence_proven=False,production_mapping_enabled=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'three shared placements; five silent native lifetimes; original FM94 tail13',flush=True)


if __name__=='__main__':main()
