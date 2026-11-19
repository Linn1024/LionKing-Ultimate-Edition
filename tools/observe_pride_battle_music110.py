"""Timestamp current battle track command against ordinary native hyena actions."""
import csv
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

base=ROOT/'build/pride-hyena-probe103';bp=base/'build-report.json';b=bound(bp)
original=ROOT/'build/pride-hyena-probe103/fights104/report.json';ref=bound(original);assert ref['result']=='PASS'
out=ROOT/'build/pride-battle-music110';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
source=ROOT/'tools/pride_battle_music_observer110.c';cmd=b['compiles']['probe'].copy()
for flag,value in [('-c',source),('-o',out/'observer.obj'),('-MT',out/'observer.obj'),('-MF',out/'observer.d')]:cmd[cmd.index(flag)+1]=str(value)
subprocess.run(cmd,cwd=cwd,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];inputs.insert(0,(out/'observer.obj').as_posix());inputs+=['-Wl,--wrap=TlkMdSoundCommand']
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,check=True)
cmd=ref['commands']['native'].copy();cmd[0]=str(out/'player.exe')
for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
with (out/'resources.ini').open('a') as f:f.write('\naudio.music.pride_lands = md\n')
for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
env.update(SDL_VIDEODRIVER='dummy',TLK_BATTLE_MUSIC_OBSERVER=str(out/'commands.csv'),TLK_WRAM_DIR=str(out),TLK_WRAM_DUMP=','.join(map(str,range(3700,3951))))
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
rows=[]
for field in range(3700,3951):
    ram=(out/f'hl_wram_{field}.bin').read_bytes();word=lambda at:struct.unpack_from('<H',ram,at)[0];ptr=lambda at:int.from_bytes(ram[at:at+3],'little')
    rows.append(dict(field=field,scene=ptr(0xdf),action=ptr(0xba43),timer=word(0xba3f),audio_wait=word(0xabf),x=word(0xba1b),y=word(0xba1d),player_x=word(0xb21b),player_y=word(0xb21d)))
(out/'frames.json').write_text(json.dumps(rows,indent=2)+'\n')
calls=list(csv.DictReader((out/'commands.csv').open()));battle=[r for r in calls if r['selector']=='1' and r['value']=='134']
jumps=[r for r in rows if r['action']==0xc148b6]
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda p:re.findall(pattern,p.read_text())
checks=dict(exit=rc==0,all4320_guest_fields_preserved=hashes(out/'run.log')==hashes(original.parent/'native/run.log'),
    battle_music_and_first_jump_observed=bool(battle) and bool(jumps),all251_snapshots=len(rows)==251)
paths=[Path(__file__),bp,original,source,rsp]
(out/'report.json').write_text(json.dumps(dict(result='BATTLE_MUSIC_TIMELINE_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,battle_music_calls=battle,
    first_native_weak_jump=jumps[0] if jumps else None,command=cmd,observer_or_selected_music_guest_writes=False,
    scope='Current103 with only MD Pride music selected, ordinary Normal inputs, compared with own current native control. This timestamps actual current behavior; original MD counterpart separately captured109.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Music timeline',checks,'battle',battle,'first jump',jumps[:1],flush=True)
