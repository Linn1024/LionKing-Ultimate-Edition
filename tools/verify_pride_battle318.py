"""Focused opening-jump cue and unchanged guest/native-audio verification."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

out=ROOT/'build/pride-battle318';out.mkdir(exist_ok=True)
build=ROOT/'build/pride-battle317/build-report.json';bound(build)
reference=ROOT/'build/pride-battle-music112/report.json';ref=bound(reference)
assets=json.loads((ROOT/'build/pride-native-hud309-runtime/report.json').read_text())['commands']['default-new']
commands={}
def run(label):
    folder=out/label;folder.mkdir(exist_ok=True)
    cmd=ref['command'].copy();cmd[0]=str(ROOT/('build/pride-native-hud307-installed/player.exe' if label.endswith('old') else 'build/pride-battle317/player.exe'))
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    if label.startswith('native'):(folder/'resources.ini').write_text('schema = 1\ngame = snes\n')
    cmd[cmd.index('--frames')+1]='3880'
    cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(3800,3881)))
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
    for flag in ('--caption-assets','--checkpoint-assets','--revival-assets','--native-hud-assets'):cmd += [flag,assets[assets.index(flag)+1]]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env.update(SDL_VIDEODRIVER='dummy',TLK_BATTLE_MUSIC_TRACE=str(folder/'jump.csv'))
    if label=='md-lle':cmd+=['--lle']
    commands[label]=cmd
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    print(label,'exit',rc,flush=True);return label,rc
with ThreadPoolExecutor(max_workers=2) as pool:exits=dict(pool.map(run,['md-old','md-new','md-lle','native-old','native-new']))
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda label:re.findall(pattern,(out/label/'run.log').read_text())
jumps={label:list(csv.DictReader((out/label/'jump.csv').open())) if (out/label/'jump.csv').exists() else [] for label in ('md-new','md-lle','native-new')}
checks=dict(exits=all(v==0 for v in exits.values()),guest_unchanged=len(hashes('md-new'))==81 and hashes('md-new')==hashes('md-old')==hashes('md-lle')==hashes('native-old')==hashes('native-new'),
    compiled_jump=len(jumps['md-new'])==1 and jumps['md-new'][0]['field']=='3852' and jumps['md-new'][0]['music_track']=='134' and jumps['md-new'][0]['audio_wait']=='0',
    interpreter_jump=jumps['md-lle']==jumps['md-new'],native_audio_unchanged=digest(out/'native-old/audio.wav')==digest(out/'native-new/audio.wav'),md_audio_changed=digest(out/'md-old/audio.wav')!=digest(out/'md-new/audio.wav'))
paths=[Path(__file__),build,reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,jumps=jumps,commands=commands,scope='Only opening cue route; 81 guest fields around encounter, native soundtrack unchanged, AOT/LLE hook agreement. No unrelated level or compatibility suites.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
