"""Bind valid route/window observations without claiming polled save replay."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
route=ROOT/'build/pride381-route/report.json';r=bound(route)
window=ROOT/'build/pride383-window/report.json';w=bound(window)
build=ROOT/'build/pride382/build-report.json';b=bound(build)
helper=ROOT/'build/pride380/report.json';assert bound(helper)['result']=='PASS'
checks={k:v for k,v in r['checks'].items() if k!='outdated_data_requests_setup'}
checks.update({k:v for k,v in w['checks'].items() if k!='current_fight_guest'})
assert all(checks.values())
out=ROOT/'build/pride384-qualification';out.mkdir(exist_ok=True)
paths=[Path(__file__),route,window,build,helper,ROOT/'build/pride383-window/fight.png']
(out/'report.json').write_text(json.dumps(dict(result='PASS',checks=checks,scope='Installed contact/palette parity, first-level route to level1, before/after guest/picture/audio and inspected real Windows boss scene. All game link objects retained in382; frontend differs only by early invalid-data guard. No claim of cold polled replay equivalence.',excluded_claims={'381_outdated_exit':'Initial host returned caption-package error6 after scene load failed; corrected early guard returns8 in382, observed383.','383_current_fight_guest':'Harness restarted full polled tape at poll0 after loading field3750. The 99 subsequent controls differ from the uninterrupted route. Retain the failed report; no game/save change is justified. Windows capture remains valid presentation evidence.'},full_first_level_complete=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS focused install/route/window qualification; no save replay claim.')
