"""Check every captured camera/latch row through live edits and current loads."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    source=ROOT/'build/pride-background-lifecycle54/report.json';prior=bound(source);assert prior['result']=='PASS'
    out=source.parent/'history-qualification';out.mkdir();checks={};counts={};paths=[Path(__file__),source]
    expected={f'{width}-{point}' for width in (256,320) for point in (1200,2200,4000)}
    checks['all_six_expected_contexts']=set(prior['observations'])==expected
    scenes=set()
    for name,data in prior['observations'].items():
        rows={stage:list(csv.DictReader((source.parent/name/stage/'background.csv').open())) for stage in ('control','live','resume')}
        point=int(name.split('-')[1]);snapshots=data['snapshots'];initial=snapshots['initial-md']
        scenes.add(initial['descriptor'])
        checks[name+'_full_camera_and_latch_trace_unchanged']=len(rows['control'])==point+30 and rows['control']==rows['live']
        checks[name+'_all30_resumed_camera_and_latch_rows']=len(rows['resume'])==30 and rows['resume']==rows['control'][-30:]
        siblings=lambda r:{c[0]:c[1:] for c in r['choices'] if c[0]!='graphics.scenery.background'}
        checks[name+'_every_other_resource_unchanged']=all(siblings(r)==siblings(initial) for r in snapshots.values())
        counts[name]=dict(full_trace_fields=len(rows['control']),resumed_fields=len(rows['resume']),
                          world_strip_pixels_changed=data['changed_world_strip_pixels'])
        paths += [source.parent/name/stage/'background.csv' for stage in rows]
    checks['both_pride_scene_descriptors_observed']=scenes=={0xc00387,0xc0080d}
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,counts=counts,
                original_layer_or_edge_equivalence_newly_claimed=False,new_renderer_or_capability_changes=False,
                cross_build_save_compatibility_tested=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
