"""Focused caption placement snapshots; no whole-game regression runs."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes

build=ROOT/'build/pride-caption268/build-report.json';b=bound(build)
reference=ROOT/'build/pride-menu227-integrated-windows/report.json';ref=bound(reference)
out=ROOT/'build/pride-caption269';out.mkdir();commands={};checks={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
for width,art,field in ((320,'snes',964),(320,'snes',1050),(256,'snes',1050),(320,'md',1050),(256,'md',1050)):
    for version in ('old','new'):
        name=f'{width}-{art}-{field}-{version}';folder=out/name;folder.mkdir();cmd=ref['command'].copy()
        cmd[0]=str(ROOT/('build/pride-menu260-help/player.exe' if version=='old' else 'build/pride-caption268/player.exe'))
        (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        (folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\ngraphics.titles.pride_lands.frames = '+art+'\n')
        for flag,value in (('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--frames',field),('--hash-at',field)):cmd[cmd.index(flag)+1]=str(value)
        i=cmd.index('--input');cmd[i]='--input-polled';cmd[i+1]=str(ROOT/'engine/tapes/allbugsF.read.tape')
        cmd+=['--dump-window',str(folder/'window.png'),'--dump-scene',str(folder/'scene.json')];commands[name]=cmd
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0;assert rc==0,name
    old=out/f'{width}-{art}-{field}-old';new=out/f'{width}-{art}-{field}-new'
    checks[f'{width}-{art}-{field}_guest_unchanged']=hashes(old/'run.log')==hashes(new/'run.log')
    print(width,art,field,'guest unchanged',checks[f'{width}-{art}-{field}_guest_unchanged'],flush=True)
paths=[Path(__file__),build,reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Five focused opening snapshots, old/new guest hashes. Both artwork choices and viewport widths plus falling-letter entrance. Pixel placement and actual Windows view inspected separately; no broad regression claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',flush=True)
