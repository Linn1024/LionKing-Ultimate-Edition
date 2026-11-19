"""Focused installed caption playback equivalence and explicit missing-data errors."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
reference=ROOT/'build/pride-caption270-clamp/report.json';ref=bound(reference)
build=ROOT/'build/pride-caption277-installed/build-report.json';b=bound(build)
out=ROOT/'build/pride-caption279-runtime';out.mkdir();checks={};commands={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
for name,prior in ref['commands'].items():
    if not name.endswith('-new'):continue
    folder=out/name;folder.mkdir();cmd=prior.copy();cmd[0]=str(build.parent/'player.exe');cmd+=['--caption-assets',str(build.parent/'captions.assets')]
    for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
    for flag,file in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/file)
    commands[name]=cmd
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    checks[name+'_exit_and_prepared_load']=rc==0 and 'caption_assets=loaded' in (folder/'run.log').read_text()
    checks[name+'_guest_exact']=hashes(folder/'run.log')==hashes(reference.parent/name/'run.log')
    for file in ('window.png','scene.json'):checks[name+'_'+file+'_exact']=digest(folder/file)==digest(reference.parent/name/file)
    print(name,rc,flush=True)
for kind in ('missing','truncated'):
    folder=out/kind;folder.mkdir();cmd=commands['320-snes-1050-new'].copy()
    for flag in ('--dump-window','--dump-scene'):
        i=cmd.index(flag);del cmd[i:i+2]
    package=folder/'caption.assets'
    if kind=='truncated':package.write_bytes((build.parent/'captions.assets').read_bytes()[:-1])
    cmd[cmd.index('--caption-assets')+1]=str(package);cmd[cmd.index('--frames')+1]='1';cmd[cmd.index('--hash-at')+1]='1'
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    text=(folder/'run.log').read_text();checks[kind+'_explicit_setup_error_before_guest']=rc==6 and 'Installed caption data is missing or incompatible. Run Setup.' in text and 'frame=1 frame_sha256=' not in text
    commands[kind]=cmd
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Five targeted caption snapshots (widths, artwork, falling/settled) preserve whole client, guest hashes and scene using prepared data. Missing/damaged data rejects before field1; no decoding fallback. No unrelated gameplay suites.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
