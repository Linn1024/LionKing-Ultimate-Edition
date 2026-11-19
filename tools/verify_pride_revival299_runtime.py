"""Focused default/checkpoint revival and fresh same-build restoration."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
reference=ROOT/'build/pride-checkpoint289-runtime/report.json';ref=bound(reference)
build=ROOT/'build/pride-revival297-installed/build-report.json';bound(build)
out=ROOT/'build/pride-revival299-runtime';out.mkdir();checks={};commands={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
for case,width,art,field,tape,polled in (
    ('default',320,'md',2070,ROOT/'build/pride-default-revival/windows/256-native-aot-3000/default-neutral.tape',False),
    ('checkpoint',256,'snes',4730,ROOT/'build/pride-checkpoint-revival/snes/revival.polled.tape',True)):
    for version in ('old','new'):
        name=case+'-'+version;folder=out/name;folder.mkdir();cmd=ref['commands']['320-md-snes-3285-new'].copy()
        cmd[0]=str(ROOT/('build/pride-checkpoint287-installed/player.exe' if version=='old' else 'build/pride-revival297-installed/player.exe'))
        i=cmd.index('--input-polled');cmd[i]='--input-polled' if polled else '--input';cmd[i+1]=str(tape)
        cmd[cmd.index('--frames')+1]=str(field);cmd[cmd.index('--hash-at')+1]=str(field)
        (folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
        (folder/'resources.ini').write_text(f'schema = 1\ngame = snes\ndisplay.viewport = {"md" if width==320 else "snes"}\ngameplay.levels.pride_lands.health_death = md\ngraphics.sprites.simba.cub.frames = {art}\ngraphics.sprites.simba.cub.palette = {art}\n')
        for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/file)
        if version=='new':
            cmd+=['--revival-assets',str(build.parent/'revival.assets')]
            if case=='default':cmd+=['--save-at','2053',str(out/'current-revival.state')]
        commands[name]=cmd
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0;assert rc==0,(name,rc)
        print(name,rc,flush=True)
    old=out/(case+'-old');new=out/(case+'-new')
    checks[case+'_guest_exact']=hashes(old/'run.log')==hashes(new/'run.log')
    for file in ('window.png','scene.json'):checks[case+'_'+file+'_exact']=digest(old/file)==digest(new/file)
    checks[case+'_installed_revival_loaded']='revival_assets=loaded' in (new/'run.log').read_text()
folder=out/'cold';folder.mkdir();cmd=commands['default-new'].copy();i=cmd.index('--save-at');del cmd[i:i+3]
cmd+=['--load',str(out/'current-revival.state')]
for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
for flag,file in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/file)
with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
checks['cold_exit']=rc==0;commands['cold']=cmd
checks['cold_guest_exact']=hashes(folder/'run.log')==hashes(out/'default-new/run.log')
for file in ('window.png','scene.json'):checks['cold_'+file+'_exact']=digest(folder/file)==digest(out/'default-new'/file)
checks['same_build_owned_checkpoint_written']=(out/'current-revival.state').stat().st_size>100000 and 'loaded_state=' in (folder/'run.log').read_text()
folder=out/'missing';folder.mkdir();cmd=commands['default-new'].copy();i=cmd.index('--save-at');del cmd[i:i+3]
for flag in ('--dump-window','--dump-scene'):
    i=cmd.index(flag);del cmd[i:i+2]
cmd[cmd.index('--revival-assets')+1]=str(folder/'missing.assets');cmd[cmd.index('--frames')+1]='1';cmd[cmd.index('--hash-at')+1]='1'
with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW).returncode
text=(folder/'run.log').read_text();checks['missing_error_before_guest']=rc==6 and 'Installed revival data is missing or incompatible. Run Setup.' in text and 'frame=1 frame_sha256=' not in text
paths=[Path(__file__),reference,build,ROOT/'build/pride-default-revival/windows/256-native-aot-3000/default-neutral.tape',ROOT/'build/pride-checkpoint-revival/snes/revival.polled.tape']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Two ordinary revival snapshots default320/MD artwork and checkpoint256/native artwork, old/new whole-client/guest/scene equality. Fresh current-build mid-revival save/cold restore exercises prepared image clone staging. Missing installed data rejects before field1; no old-build save or audio-tail claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
