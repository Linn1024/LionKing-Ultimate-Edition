"""Audit same-field original fatal dispatch, preserving rejected hypotheses."""
import csv
import json
from pathlib import Path

from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_bounce_owner_preview_history import bound


def main():
    base=ROOT/'build/pride-fatal-entry-audit';base.mkdir()
    first_path=ROOT/'build/pride-fatal-entry/report.json'
    flags_path=ROOT/'build/pride-fatal-entry-flags/report.json'
    first=bound(first_path);flags=bound(flags_path)
    expected_first={f'{name}/same_field_dispatch_retains_actor_state' for name in ('default','checkpoint')}
    expected_flags={f'{name}/{check}' for name in ('default','checkpoint')
        for check in ('only_original_post_actor_flag_differs','original_post_actor_flag_write_observed')}
    checks=dict(first_rejected_hypothesis_exact={k for k,v in first['checks'].items() if not v}==expected_first,
        writer_capture_rejected_transcription_exact={k for k,v in flags['checks'].items() if not v}==expected_flags)
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    # Original MOVE.B $43(A0),$44(A0), immediately before the journal's PC.
    checks['original_flag_history_copy_instruction']=rom[0x7de2a:0x7de30]==bytes.fromhex('116800430044')
    cases={};paths=[Path(__file__),first_path,flags_path]
    for name in ('default','checkpoint'):
        case=flags['cases'][name];events=case['events'];death=case['death']
        original=first['cases'][name]
        checks[name+'/read_only_writer_observer_preserves_all_entry_records']=events==original['events']
        checks[name+'/all_events_same_fatal_field']=all(int(row['field'])==death for row in events)
        checks[name+'/call_return_dispatch_order']=[r['event'] for r in events]==[
            'hit_select','fatal_hurt_entry','fatal_hurt_return','death_dispatch']
        a=events[2];b=events[3]
        before=[int(a['actor_words'][at:at+4],16) for at in range(0,256,4)]
        after=[int(b['actor_words'][at:at+4],16) for at in range(0,256,4)]
        differences=[dict(offset=i*2,before=x,after=y) for i,(x,y) in enumerate(zip(before,after)) if x!=y]
        checks[name+'/only_original_history_byte_changes']=differences==[dict(offset=0x44,before=0,after=0x400)]
        checks[name+'/history_source_byte_matches']=before[0x42//2]&255==4
        path=flags_path.parent/name/'writes.csv';paths.append(path)
        writes=list(csv.DictReader(path.open()))
        history=[r for r in writes if int(r['field'])==death and r['pc']=='07de30' and
            r['width']=='1' and int(r['address'],16)==0xffff9412 and int(r['value'],16)==4]
        checks[name+'/executed_original_history_write']=len(history)==1
        checks[name+'/position_velocity_timer_action_retained']=all(a[k]==b[k] for k in ('x','y','vx','vy','timer','action'))
        checks[name+'/one_life_consumed_before_dispatch']=int(a['lives'])-int(b['lives'])==1
        checks[name+'/hurt_initializes_at_zero']=a['health']==b['health']=='0' and a['timer']=='18' and a['vy']=='fffd0000'
        checks[name+'/prefix_controls_complete']=case['prefix_wram_controls']==case['prefix']//100
        cases[name]=dict(field=death,position=[int(a['x']),int(a['y'])],action=a['action'],timer=18,
            motion_before_dispatch=[a['vx'],a['vy']],actor_word_differences=differences,
            original_history_writes=history,extra_video_fields_before_dispatch=0)
        for field in (death-1,death,death+1,death+2):
            source=first_path.parent/name/f'wram-{field}.bin';observed=flags_path.parent/name/f'wram-{field}.bin'
            checks[f'{name}/full_wram_writer_observer_neutral_{field}']=source.read_bytes()==observed.read_bytes()
            paths += [source,observed]
    report=dict(result='ORIGINAL_SAME_FIELD_FATAL_DISPATCH_VERIFIED' if all(checks.values()) else 'FAIL',
        checks=checks,cases=cases,ordinary_original_inputs=True,guest_mutations=False,
        original_18_tick_timer_is_not_an_18_field_predeath_delay=True,
        visible_effect_of_initial_hurt_state_proven=False,
        current_standalone_nonfinal_health_death_already_integrated=True,
        production_changes=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (base/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks; failures',[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
