"""Keep251 failure and correct its native-timing idle assumption for MD timeout."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

source=ROOT/'build/pride-menu251-md-routes/report.json';old=bound(source)
failed=[k for k,v in old['checks'].items() if not v]
expected=[f'{width}-idle-{mode}_endpoint_art_or_retirement' for width in (256,320) for mode in ('aot','lle')]
assert old['result']=='FAIL' and sorted(failed)==sorted(expected)
out=ROOT/'build/pride-menu262-md-routes';out.mkdir()
checks={k:v for k,v in old['checks'].items() if k not in failed};observations={}
for width in (256,320):
    control=source.parent/f'{width}-idle-control'
    for mode in ('aot','lle'):
        name=f'{width}-idle-{mode}';folder=source.parent/name
        scene=json.loads((folder/'scene.json').read_text())
        checks[name+'_retired_to_same_title_client']=digest(folder/'window.png')==digest(control/'window.png') and scene['latched_gameplay']['descriptor']==0x5ab and not scene['stage_detected']
        observations[name]=dict(endpoint_descriptor=scene['latched_gameplay']['descriptor'],stage_detected=scene['stage_detected'])
paths=[Path(__file__),source,ROOT/'docs/pride-continue-timeout.md',ROOT/'engine/runner/tlk_continue_menu.h',ROOT/'engine/runner/pride/final/pride_final_runtime.inc']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=old['commands'],
    correction='251 incorrectly expected idle artwork to remain at field6000, applying native credit-bearing no-timeout behavior to selected MD timing. Existing original-backed MD timeout policy returns to title. Retained clients show descriptor0005AB/title and equal controls. Correct endpoint expectation only; no runtime changes, recaptures, source-clock equivalence or erased failure.',
    scope='All24 original251 executions retain exact2501 guest fields/whole PCM/scenes and mode clients; YES/NO/GameOver retirement plus idle timeout-to-title. Intermediate menu whole-window pixels are separately verified by246/247, not this endpoint matrix.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
