"""Qualify MD actor cadence while explicitly retaining native task/frame pacing."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-checkpoint-animation52';out=base/'cadence-qualification';out.mkdir()
    playpath=base/'animation-play/report.json';play=bound(playpath)
    completionpath=base/'completion/report.json';completion=bound(completionpath)
    uipath=base/'windows-ui/report.json';ui=bound(uipath)
    referencepath=ROOT/'build/pride-checkpoint-timing51-qualification/report.json';reference=bound(referencepath)
    rows=list(csv.DictReader((base/'animation-play/cycles-aot/timing.csv').open()))
    updates=0;phases=[];calls=[]
    for row in rows:
        if row['pc']=='c55750':updates+=1;calls.append(int(row['field']))
        elif row['pc']=='c0ad54':phases.append(dict(update=updates,**row))
    starts=[r['update'] for r in phases if r['phase']=='0']
    gaps=[dict(before=a,after=b,missing_fields=b-a-1) for a,b in zip(calls,calls[1:]) if b-a>1]
    checks=dict(
        original_reference_bound=reference['result']=='PASS',
        rejected_only_unconditional_display_clock_assumption=[k for k,v in play['checks'].items() if not v]==['display_3729'],
        full_first_level_route_passes=completion['result']=='PASS' and all(completion['checks'].values()),
        actual_windows_ui_and_restart_pass=ui['result']=='PASS' and all(ui['checks'].values()),
        each_phase_uses_original_md_duration=all(
            int(r['value'])==[5,20,5,90,90,5][int(r['phase'])] for r in phases),
        phase_order_repeats=all(int(r['phase'])==i%6 for i,r in enumerate(phases)),
        three_complete_221_update_cycles=len(starts)>=4 and [b-a for a,b in zip(starts,starts[1:])]==[221,221,221],
        duration_plus_one_countdown=all(b['update']-a['update']==int(a['value'])+1 for a,b in zip(phases,phases[1:])),
        first_visible_blink_matches_md_contact_offset=next(c['field'] for c in play['captures'] if c['poses']==[0xc2fde1]) -3280==7,
        initial_base_four_waits=list(csv.DictReader((base/'animation-play/md-contact/timing.csv').open()))[0]['value']=='4',
        native_task_gaps_are_observed=gaps==[dict(before=3284,after=3286,missing_fields=1),
                                           dict(before=3572,after=3574,missing_fields=1),
                                           dict(before=3592,after=3594,missing_fields=1)],
        native_source_all6000_fields_unchanged=completion['checks']['native_all6000_guest_fields_unchanged'],
        modified_modes_all6000_fields_exact=completion['checks']['all6000_guest_fields_mode_parity'],
        shared_sun_hook_still_runs=play['checks']['sun_shared_parser_hook_still_runs'])
    paths=[Path(__file__),playpath,completionpath,uipath,referencepath]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                scope='Original MD per-actor-update cadence with native task flags and frame scheduling retained; first visible contact offset matched',
                phase_entries=phases,native_task_field_gaps=gaps,
                exact_md_display_clock_equivalence_verified=False,
                rejected_display_assumption_retained_in=playpath.relative_to(ROOT).as_posix(),
                publication_ready=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
