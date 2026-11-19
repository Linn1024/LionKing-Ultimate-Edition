"""Inspect visible native opening titles outside Pride using ordinary practice UI."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/level-caption340';out.mkdir(exist_ok=True)
r=json.loads((ROOT/'build/pride-porcupine328/report.json').read_text());commands={}
for level in (1,2):
    folder=out/str(level);folder.mkdir(exist_ok=True);cmd=r['commands']['native-new'].copy()
    i=cmd.index('--input-polled');del cmd[i:i+2]
    cmd+=['--practice-level',str(level)];cmd[cmd.index('--frames')+1]='1800';cmd[cmd.index('--hash-at')+1]='1800'
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes((ROOT/'build/pride-porcupine328/native-new'/name).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    with (folder/'resources.ini').open('a') as f:f.write('display.viewport = md\n')
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
    with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    commands[str(level)]=cmd
    scene=json.loads((folder/'scene.json').read_text());print(level,rc,scene['level'],scene['latched_gameplay'],flush=True)
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED',commands=commands,source_sha256={Path(__file__).resolve().relative_to(ROOT).as_posix():digest(Path(__file__))}),indent=2)+'\n')
