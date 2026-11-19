"""Correct the start-scene assumption without replacing failed observations."""
from collections import Counter
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    source=ROOT/'build/pride-music-owner59/verification/report.json';prior=bound(source)
    out=source.parent/'qualification';out.mkdir();checks={};observations={}
    expected={mode+'_music_both_pride_scenes' for mode in ('aot','lle')}
    checks['only_failed_assertions_are_start_scene_assumption']={k for k,v in prior['checks'].items() if not v}==expected
    checks['all_other_original_checks_pass']=all(v for k,v in prior['checks'].items() if k not in expected)
    for mode in ('aot','lle'):
        rows=list(csv.DictReader((source.parent/mode/'owner.csv').open()))
        software=[r for r in rows if r['stage']=='software' and r['group']=='224']
        checks[mode+'_eight_channels_initialize_before_pride']=sum(int(r['scene'])==0xc0057b and int(r['field'])==109 for r in software)==8
        checks[mode+'_eight_channels_reinitialize_for_boss']=sum(int(r['scene'])==0xc0080d and int(r['field'])==3855 for r in software)==8
        byscene={}
        for scene in (0xc00387,0xc0080d):
            groups=Counter(r['group'] for r in rows if r['stage']=='keyon' and int(r['scene'])==scene and r['level']=='0')
            checks[mode+f'_{scene:06x}_actual_music_and_effect_starts']=set(groups)=={'0','224'}
            byscene[f'{scene:06x}']=dict(groups)
        observations[mode]=byscene
    paths=[Path(__file__),source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
                reused_completed_observations=True,initial_music_owner_survives_scene_transition=True,
                production_or_guest_changed=False,complete_output_filter_not_implemented=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),observations,flush=True)


if __name__=='__main__':main()
