"""Reproduce the caption at the left camera clamp using ordinary neutral input."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
reference=ROOT/'build/pride-caption269/report.json';ref=bound(reference)
out=ROOT/'build/pride-caption270-clamp';out.mkdir();checks={};commands={}
tape=out/'idle.polled.tape';source=ROOT/'engine/tapes/allbugsF.read.tape';tape.write_bytes(source.read_bytes()[:638*2]+bytes(10000))
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
for width,art,field in ((320,'snes',964),(320,'snes',1050),(256,'snes',1050),(320,'md',1050),(256,'md',1050)):
    for version in ('old','new'):
        name=f'{width}-{art}-{field}-{version}';folder=out/name;folder.mkdir();cmd=ref['commands'][name].copy()
        for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
            text=Path(cmd[cmd.index(flag)+1]).read_text()
            (folder/file).write_text(text);cmd[cmd.index(flag)+1]=str(folder/file)
        cmd[cmd.index('--input-polled')+1]=str(tape)
        for flag,file in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/file)
        commands[name]=cmd
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        assert rc==0,(name,rc)
    old=out/f'{width}-{art}-{field}-old';new=out/f'{width}-{art}-{field}-new'
    checks[f'{width}-{art}-{field}_guest_unchanged']=hashes(old/'run.log')==hashes(new/'run.log')
    checks[f'{width}-{art}-{field}_at_left_clamp']=json.loads((new/'scene.json').read_text())['camera'][0]==0
    print(width,art,field,flush=True)
paths=[Path(__file__),reference,source]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Five targeted opening snapshots at actual left camera clamp with ordinary neutral controller input. Both widths/artwork and falling entrance; guest state preserved. Visual centring inspected separately.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
