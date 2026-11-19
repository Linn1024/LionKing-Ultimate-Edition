"""Only checkpoint contact/animation snapshots and missing-package startup check."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
reference=ROOT/'build/pride-caption279-runtime/report.json';ref=bound(reference)
build=ROOT/'build/pride-checkpoint287-installed/build-report.json';bound(build)
out=ROOT/'build/pride-checkpoint289-runtime';out.mkdir();checks={};commands={};observations={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
for width,frames,timing,field in ((320,'md','snes',3285),(320,'md','md',3308),(256,'snes','snes',3290)):
    case=f'{width}-{frames}-{timing}-{field}'
    for version in ('old','new'):
        name=case+'-'+version;folder=out/name;folder.mkdir();cmd=ref['commands']['320-snes-1050-new'].copy()
        cmd[0]=str(ROOT/('build/pride-caption277-installed/player.exe' if version=='old' else 'build/pride-checkpoint287-installed/player.exe'))
        cmd[cmd.index('--input-polled')+1]=str(ROOT/'engine/tapes/allbugsF.read.tape')
        cmd[cmd.index('--frames')+1]=str(field);cmd[cmd.index('--hash-at')+1]=str(field)
        (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        (folder/'resources.ini').write_text(f'schema = 1\ngame = snes\ndisplay.viewport = {"md" if width==320 else "snes"}\ngraphics.sprites.checkpoints.frames = {frames}\ngraphics.sprites.checkpoints.palette = md\ngameplay.levels.pride_lands.checkpoint_animation = {timing}\n')
        for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/file)
        if version=='new':cmd+=['--checkpoint-assets',str(build.parent/'checkpoints.assets')]
        commands[name]=cmd
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0;assert rc==0,(name,rc)
    old=out/(case+'-old');new=out/(case+'-new');scene=json.loads((new/'scene.json').read_text())
    checks[case+'_prepared_load']='checkpoint_assets=loaded' in (new/'run.log').read_text()
    checks[case+'_guest_exact']=hashes(old/'run.log')==hashes(new/'run.log')
    for file in ('window.png','scene.json'):checks[case+'_'+file+'_exact']=digest(old/file)==digest(new/file)
    poses=[p['pose'] for p in scene['pieces'] if p['pose'] in (0xc456de,0xc2fde1,0xc2fe18) and p['kept']]
    checks[case+'_checkpoint_visible_in_scene']=bool(poses);observations[case]=poses
    print(case,'visible poses',poses,flush=True)
folder=out/'missing';folder.mkdir();cmd=commands['320-md-snes-3285-new'].copy()
for flag in ('--dump-window','--dump-scene'):
    i=cmd.index(flag);del cmd[i:i+2]
cmd[cmd.index('--checkpoint-assets')+1]=str(folder/'missing.assets');cmd[cmd.index('--frames')+1]='1';cmd[cmd.index('--hash-at')+1]='1'
with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW).returncode
text=(folder/'run.log').read_text();checks['missing_explicit_error_before_guest']=rc==6 and 'Installed checkpoint data is missing or incompatible. Run Setup.' in text and 'frame=1 frame_sha256=' not in text
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
    scope='Three focused ordinary checkpoint snapshots, two widths and source/timing mixtures. Whole clients/scene and guest hashes compared against277; no gameplay changes or unrelated suites.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
