"""Separate display timing and incoming subpixels from ledge movement evidence."""
import csv
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_preview_history import bound


def main():
    base=ROOT/'build/pride-ledge-physics';out=base/'comparison';out.mkdir()
    paths=[base/f'{source}/report.json' for source in ('snes','md')]
    snes,md=[bound(p) for p in paths]
    checks={'native_observer_neutral':snes['every_observed_field_matches_public']}
    fields=('x','y','timer','vx','vy')
    cases={}
    for name,a in snes['cases'].items():
        b=md['cases'][name]
        differences=[dict(relative_field=i+1,values={k:[x[k],y[k]] for k in fields if x[k]!=y[k]})
            for i,(x,y) in enumerate(zip(a,b)) if any(x[k]!=y[k] for k in fields)]
        first_exit=lambda rows,action:next((i+1 for i,r in enumerate(rows) if r['action']!=action),None)
        cases[name]=dict(observed_fields_per_original=len(a),literal_differences=differences,
            first_exit_native=first_exit(a,'c33d1f'),first_exit_md=first_exit(b,'194b94'))
        checks[name+'/length']=len(a)==len(b)==120
        # Only compare the initial countdown, before its sentinel/loop semantics.
        def countdown(rows):
            values=[]
            for r in rows:
                value=int(r['timer'])
                if not values or value!=values[-1]:values.append(value)
                if value==0:break
            return values
        if name not in ('down','roll'):
            checks[name+'/initial_countdown']=countdown(a)==countdown(b)==list(range(41,-1,-1))
            cases[name]['native_initial_timer_holds']=[i+1 for i in range(1,44)
                if a[i]['timer']==a[i-1]['timer'] and int(a[i]['timer'])>0]
        elif name in ('down','roll'):
            checks[name+'/same_immediate_drop']=cases[name]['first_exit_native']==cases[name]['first_exit_md']==1
    # Historical RAM is accepted only when present byte-for-byte in the freshly
    # captured COMPLETE core states. Never edit fractions to manufacture parity.
    raw_paths=[ROOT/'build/native-pickup-flight/hl_wram_1472.bin',
               ROOT/'build/pride-cub-contact-audio/wram-1874.bin']
    raw=[p.read_bytes() for p in raw_paths]
    for source,data in zip(('snes','md'),raw):
        checks[source+'/historical_ram_exact_in_fresh_snapshot']=(base/f'{source}/ledge.state').read_bytes().count(data)==1
    fractions=[struct.unpack_from('<H',data,actor+0x36)[0] for data,actor in zip(raw,(0xb213,0x93ce))]
    checks['different_incoming_y_fractions']=fractions==[0x8c00,0xba00]
    arithmetic={}
    for name in ('down','roll'):
        sequences=[]
        for report,fraction in zip((snes,md),fractions):
            fixed=(int(report['initial']['y'])+48)*65536+fraction
            predicted=[]
            for row in report['cases'][name][:11]:
                fixed+=int(row['vy'],16)
                predicted.append(fixed>>16)
            actual=[int(r['y']) for r in report['cases'][name][:11]]
            sequences.append(dict(predicted=predicted,observed=actual))
        arithmetic[name]=sequences
        checks[name+'/incoming_subpixel_explains_first_11_fields']=all(r['predicted']==r['observed'] for r in sequences)
    loop_path=base/'scene-loop/report.json';loop=bound(loop_path)
    rows=list(csv.DictReader((loop_path.parent/'loop.csv').open()))
    completed=[int(r['field'])-1472 for r in rows]
    checks['scene_loop_observer_neutral']=loop['every_120_guest_fields_matches_public']
    checks['118_scene_returns_in_120_display_fields']=len(completed)==118
    checks['two_delayed_double_returns']=[f for f in sorted(set(completed)) if completed.count(f)==2]==[13,18]
    checks['matching_climb_transition_parameters']=all(
        (snes['cases'][case][44]['timer'],md['cases'][case][42]['timer'])==('31','31')
        for case in ('up','left','reverse'))
    report=dict(result='BOUNDED_LEDGE_PROTOCOLS_AUDITED' if all(checks.values()) else 'FAIL',
        checks=checks,cases=cases,native_scene_callback_completed_fields=completed,
        initial_y_subpixels=fractions,drop_arithmetic=arithmetic,
        exact_physics_equivalence_claimed=False,display_timing_is_not_a_new_movement_rule=True,
        opposite_ledge_and_damage_interruptions_verified=False,
        production_changes=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),*paths,*raw_paths,loop_path]})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks; failures',[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
