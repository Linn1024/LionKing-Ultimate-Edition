"""Explicit native-menu save rejection preserves an existing owned file."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
seed=ROOT/'build/pride-menu233-gameplay-save/report.json';s=bound(seed);assert s['result']=='PASS'
reference=ROOT/'build/pride-menu221-wide/report.json';ref=bound(reference)
out=ROOT/'build/pride-menu235-save-guard';out.mkdir()
cmd=s['commands']['cold'].copy()
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
for flag in ('--dump-window','--dump-scene'):
    i=cmd.index(flag);del cmd[i:i+2]
cmd[cmd.index('--frames')+1]='4400';cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(4100,4401)))
sentinel=out/'existing-owned.state';sentinel.write_bytes(b'Owned save-preservation sentinel\n');before=digest(sentinel)
cmd+=['--save-at','4400',str(sentinel)]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
with (out/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
log=(out/'run.log').read_text();pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
actual=re.findall(pattern,log);expected=dict((a,(b,c)) for a,b,c in re.findall(pattern,(reference.parent/'yes-control/run.log').read_text()))
checks=dict(scripted_invalid_save_explicitly_rejected=rc==8 and 'cannot save state '+str(sentinel) in log,
    existing_file_preserved=digest(sentinel)==before,
    no_successful_save_report='saved_state=' not in log,
    all_observed_pre_rejection_guest_samples_native=len(actual)>=299 and all(expected.get(a)==(b,c) for a,b,c in actual))
paths=[Path(__file__),seed,reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,process_exit=rc,
    scope='Selected MD menu/native timing current226: scripted save during owned Continue deliberately rejected (CLI8), existing owned file intact and observed guest state native. GUI toast and arbitrary saves are not qualified here.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
