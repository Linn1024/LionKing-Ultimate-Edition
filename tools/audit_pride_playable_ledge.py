"""Audit playable opposite-ledge evidence and retain environmental divergences."""
import csv
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from capture_pride_ledge_physics import PATTERN
from pride_bounce_owner_preview_history import bound


def main():
    base=ROOT/'build/pride-ledge-controlled';out=base/'playable-comparison';out.mkdir()
    paths=[base/f'playable-opposite/{s}/report.json' for s in ('snes','md')]
    snes,md=[bound(p) for p in paths]
    finder_path=base/'find-playable/report.json';finder=bound(finder_path)
    poll_path=base/'poll-observer/report.json';poll=bound(poll_path)
    checks=dict(native_aot_lle_observer_neutral=snes['every_observed_field_matches_public_aot_lle'],
        corrected_poll_observer_passes=poll['result']=='PASS' and all(poll['checks'].values()),
        md_natural_fixture_found=finder['result']=='FOUND',
        natural_branch_26_neutral_fields=finder['found']['inputs']==[0]*26,
        same_initial_integer_position=(snes['initial']['x'],snes['initial']['y'])==(md['initial']['x'],md['initial']['y'])==(1232,481),
        same_initial_health_roar=(snes['initial']['health'],snes['initial']['roar'])==(md['initial']['health'],md['initial']['roar'])==(6,24),
        different_incoming_fractions=(snes['initial']['frac_x'],snes['initial']['frac_y'])==(0,0xda00) and
            (md['initial']['frac_x'],md['initial']['frac_y'])==(0x4000,0x6200))
    fields=('x','y','vx','vy','timer','health','roar')
    pairs={'c33f11':'194da6','c33bfd':'194a68','c32b24':'193a1c',
        'c302ef':'191278','c31ac3':'1929be','c33226':'194070','c3554c':'196406'}
    cases={}
    for name,a in snes['cases'].items():
        b=md['cases'][name]
        differences=[dict(relative_field=i+1,values={k:[x[k],y[k]] for k in fields if x[k]!=y[k]})
            for i,(x,y) in enumerate(zip(a,b)) if any(x[k]!=y[k] for k in fields)]
        state_differences=[dict(relative_field=i+1,native=x['action'],md=y['action'])
            for i,(x,y) in enumerate(zip(a,b)) if pairs.get(x['action'])!=y['action']]
        cases[name]=dict(literal_differences=differences,state_differences=state_differences)
        checks[name+'/both_120_fields']=len(a)==len(b)==120
        if name not in ('down','roll'):
            checks[name+'/all_120_physical_fields_exact']=not differences
            checks[name+'/corresponding_observed_action_path']=not state_differences
        if name in ('up','right'):
            checks[name+'/same_43_to_75_climb']=all(
                rows[41]['timer']==0 and rows[42]['timer']==31 and rows[42]['action']==climb and
                rows[74]['action']==idle and (rows[74]['x'],rows[74]['y'])==(1241,480)
                for rows,climb,idle in ((a,'c33bfd','c32b24'),(b,'194a68','193a1c')))
    drop=[]
    for data in (snes,md):
        fixed=((data['initial']['y']+48)<<16)+data['initial']['frac_y'];predicted=[]
        for row in data['cases']['down'][:8]:fixed+=row['vy'];predicted.append(fixed>>16)
        observed=[row['y'] for row in data['cases']['down'][:8]]
        drop.append(dict(predicted=predicted,observed=observed))
    checks['down/first_8_positions_explained_by_own_incoming_fraction']=all(r['predicted']==r['observed'] for r in drop)
    checks['down/rejoin_on_same_ground_at_9']=all((d['cases']['down'][8]['x'],d['cases']['down'][8]['y'])==(1220,544) for d in (snes,md))
    checks['down/after_landing_all_physical_fields_exact']=all(
        all(x[k]==y[k] for k in fields) for x,y in zip(snes['cases']['down'][8:],md['cases']['down'][8:]))
    checks['roll/contact_divergence_retained']=bool(cases['roll']['literal_differences']) and md['cases']['roll'][111]['health']==5 and snes['cases']['roll'][111]['health']==6
    for name in ('neutral','up','down','roll'):
        checks[name+'/native_120_real_pad_reads']=poll['observations']['playable-opposite'][name]['polls']==120
    # Preserve the failed candidate as transition evidence, without describing its
    # changing/reused actor slot as a playable 120-field ledge continuation.
    cut=base/'opposite/snes';cut_paths=[cut/(f'neutral-public-{mode}/run.log') for mode in ('lle','aot')]
    cut_hashes=[re.findall(PATTERN,p.read_text()) for p in cut_paths]
    cut_rows=list(csv.DictReader((cut/'neutral-observer/actor.csv').open()))
    checks['ending_fixture/all_120_native_mode_hashes_exact']=len(cut_hashes[0])==120 and cut_hashes[0]==cut_hashes[1]
    checks['ending_fixture/card_transition_at_92']=cut_rows[0]['scene']=='c0080d' and cut_rows[91]['scene']=='c005ab'
    checks['ending_fixture/rejected_by_original_capture_scene_guard']=not (cut/'report.json').exists()
    cut_md_path=base/'opposite/md/report.json';cut_md=bound(cut_md_path)
    checks['ending_fixture/md_slot_replaced_at_113']=cut_md['cases']['neutral'][112]['action']=='000000'
    paths += [finder_path,poll_path,cut_md_path,*cut_paths,cut/'neutral-observer/actor.csv',Path(__file__)]
    report=dict(result='BOUNDED_PLAYABLE_OPPOSITE_LEDGE_AUDITED' if all(checks.values()) else 'FAIL',
        checks=checks,cases=cases,drop_fraction_arithmetic=drop,
        native_first_observer_per_field_tape_poll_column_is_uninstrumented=True,
        md_initial_poll_column_after_snapshot_load_is_not_an_observation=True,
        corrected_poll_evidence=poll_path.relative_to(ROOT).as_posix(),
        ending_fixture_usable_for_full_playable_continuation=False,
        rolled_enemy_damage_equivalence_proven=False,all_ledge_art_phase_equivalence_proven=False,
        production_gameplay_changes=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks; failures',[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
