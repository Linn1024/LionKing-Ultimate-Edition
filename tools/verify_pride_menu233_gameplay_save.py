"""Current226 ordinary gameplay save/load with selected MD menu graphics."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/pride-menu227-integrated-windows/report.json';ref=bound(reference)
build=ROOT/'build/pride-menu226-integrated/build-report.json';bound(build)
assert shutil.disk_usage(ROOT).free>8*1024*1024,'Need space for current state and boot checkpoint'
out=ROOT/'build/pride-menu233-gameplay-save';out.mkdir();checks={};commands={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
state=out/'current.state';pattern=r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+'
for name in ('warm','cold'):
    folder=out/name;folder.mkdir();cmd=ref['command'].copy()
    for flag,file in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
    for flag,value in (('--frames',3800),('--hash-at',','.join(map(str,range(3601,3801))))):cmd[cmd.index(flag)+1]=str(value)
    cmd+=['--dump-window',str(folder/'window.png'),'--dump-scene',str(folder/'scene.json')]
    cmd+=['--save-at','3600',str(state)] if name=='warm' else ['--load',str(state)]
    with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=f,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    commands[name]=cmd;checks[name+'_exit']=rc==0;assert rc==0,(name,rc)
    print(name,'exit',rc,flush=True)
checks['current_state_written']=state.exists() and state.stat().st_size>100000
a=re.findall(pattern,(out/'warm/run.log').read_text());b=re.findall(pattern,(out/'cold/run.log').read_text())
checks['all200_resumed_guest_fields_exact']=a==b and len(a)==200
checks['complete_client_exact']=digest(out/'warm/window.png')==digest(out/'cold/window.png')
checks['scene_exact']=(out/'warm/scene.json').read_bytes()==(out/'cold/scene.json').read_bytes()
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Current226 ordinary gameplay save at3600/cold resume to3800 with only MD menu art and320 viewport selected.200 full guest picture/WRAM samples and client/scene match. Fresh state, no old-build compatibility or audio-tail/mid-menu save claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',checks,flush=True)
