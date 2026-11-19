"""Correct the validator's expected installed-data error code without replay."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/pride393-window/report.json';r=bound(reference)
assert all(v for k,v in r['checks'].items() if k!='old_sprite_package_requests_setup')
out=ROOT/'build/pride394-qualification';out.mkdir(exist_ok=True)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
with (out/'rejected.log').open('wb') as log:rc=subprocess.run(r['reject_command'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW).returncode
checks={k:v for k,v in r['checks'].items() if k!='old_sprite_package_requests_setup'}
checks['old_sprite_package_requests_setup']=rc==8 and 'Installed sprite data is missing or incompatible. Run Setup again.' in (out/'rejected.log').read_text()
paths=[Path(__file__),reference,ROOT/'build/pride392-route/report.json',ROOT/'build/pride391/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,reject_exit_code=rc,command=r['reject_command'],scope='Retain393 actual ordinary-play Windows observation. Its validator expected6, but the existing frontend correctly uses8 for installed-data rejection. Repeat only the one-field rejection with the correct expectation; no game change or repeated route/window run.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'rejected.log':digest(out/'rejected.log')}),indent=2)+'\n')
print(checks,flush=True)
