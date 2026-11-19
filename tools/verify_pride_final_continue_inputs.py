"""Compare player-facing Continue input decisions against the original MD game."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-final-input-comparison';out.mkdir()
    base=ROOT/'build/pride-final-input-reference/report.json'
    boundary=ROOT/'build/pride-final-input-boundary/report.json'
    first=ROOT/'build/pride-final-input-first-edge/report.json'
    native=ROOT/'build/pride-final-input-refresh-probe2/continue/report.json'
    preceding=ROOT/'build/pride-final-input-probe2/continue/report.json'
    presentation=ROOT/'build/pride-final-input-refresh-probe2/capture/report.json'
    a=bound(base);b=bound(boundary);c=bound(first);n=bound(native);p=bound(preceding);v=bound(presentation)
    references=dict(a['observations'],**b['observations'],**c['observations']);checks={};differences=[]
    for name,row in n['observations'].items():
        original=references[name]
        stops=[r['age'] for r in original['music'] if r['program']==0 and r['age']>100]
        checks[name+'/confirmation_outcome']=bool(stops)==bool(row['accepted'])
        checks[name+'/decisions_gated']=all(r['age']>=124 for r in row['decisions'])
        if stops and row['accepted']:
            differences.append(dict(case=name,original_music_stop=stops[0],native_music_stop_return=row['accepted'][0],
                                    remaining_offset=row['accepted'][0]-stops[0]))
    checks['original_edge123_ignored']=not any(r['program']==0 and r['age']>100 for r in references['edge-123']['music'])
    checks['original_edge124_accepted']=any(r['program']==0 and r['age']==165 for r in references['edge-124']['music'])
    checks['released_direction_no_longer_latched']=p['observations']['early-release']['decisions'][0]['pad']=='0200' and n['observations']['early-release']['decisions'][0]['pad']=='0000'
    game=n['observations']['after-fade']['final']
    checks['ordinary_continue_returns_to_pride']=game['descriptor']==0x387 and game['player']==[64,1255] and game['health']==4 and game['lives']==2
    checks['last_life_presentation_retained']=v['result']=='PROTOTYPE_PASS' and all(v['checks'].values())
    paths=[Path(__file__),base,boundary,first,native,preceding,presentation]
    report=dict(result='INPUT_CONTRACT_PASS' if all(checks.values()) else 'FAIL',checks=checks,
        remaining_continue_exit_timing_differences=differences,full_continue_timing_equal=False,
        public_player_changed=False,interpreter_native256_only=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'input checks; remaining',differences,flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
