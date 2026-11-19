"""Observe both entrance timers on ordinary stop and braking routes."""
import csv
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';reference=base/'fights140/report.json';ref=bound(reference);assert ref['result']=='PASS'
observer=ROOT/'build/pride-hyena-entrance149-observer';bp=observer/'build-report.json';b=bound(bp)
plan=ROOT/'build/pride-hyena-entrance145-plan/report.json';p=bound(plan);assert p['result']=='PLANNED'
out=ROOT/'build/pride-hyena-entrance150-boundary';out.mkdir();checks={};commands={};observations={}
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
def run(label,tape,frames,selected):
    folder=out/label;folder.mkdir();cmd=ref['commands']['entrance-aot' if selected else 'native'].copy();cmd[0]=str(observer/'player.exe')
    cmd[cmd.index('--frames')+1]=str(frames);cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(1,frames+1)))
    cmd[cmd.index('--input-polled')+1]=str(tape)
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
    for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_ENTRANCE_CONTEXT149=str(folder/'contexts.csv'))
    with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    assert rc==0,(label,rc)
    commands[label]=cmd;rows=list(csv.DictReader((folder/'contexts.csv').open()));observations[label]=rows
    print(label,'exit',rc,'contexts',len(rows),'last timer',rows[-1]['timer'] if rows else None,flush=True)
    return folder
normal=Path(ref['commands']['native'][ref['commands']['native'].index('--input-polled')+1])
for selected,label in [(False,'pilot-native'),(True,'pilot-md')]:
    folder=run(label,normal,4320,selected);control=reference.parent/('entrance-aot' if selected else 'native')
    checks[label+'_all4320_guest_fields_neutral']=len(hashes(folder))==4320 and hashes(folder)==hashes(control)
    checks[label+'_whole_pcm_neutral']=digest(folder/'audio.wav')==digest(control/'audio.wav')
assert all(checks.values()),checks
prefix=normal.read_bytes()[:p['polls']*2]
for name,tail in [('stop',[0]*500),('brake8',[0x200]*8+[0]*492),('brake16',[0x200]*16+[0]*484)]:
    tape=out/(name+'.polled.tape');tape.write_bytes(prefix+struct.pack('<'+'H'*len(tail),*tail))
    for selected,label in [(False,'snes'),(True,'md')]:run(name+'-'+label,tape,4194,selected)
    a={int(r['field']):r for r in observations[name+'-snes']};bb={int(r['field']):r for r in observations[name+'-md']}
    different=[dict(field=f,snes_timer=int(a[f]['timer']),md_timer=int(bb[f]['timer']),snes_player=[int(a[f]['player_x']),int(a[f]['player_y'])],md_player=[int(bb[f]['player_x']),int(bb[f]['player_y'])],snes_camera=int(a[f]['camera_x']),md_camera=int(bb[f]['camera_x'])) for f in sorted(a.keys()&bb.keys()) if a[f]['timer']!=bb[f]['timer']]
    (out/(name+'-differences.json')).write_text(json.dumps(different,indent=2)+'\n');print(name,'timer differences',len(different),different[:1],flush=True)
    if different:break
paths=[Path(__file__),reference,bp,plan]
checks['ordinary_inputs_and_actual_contexts']=all(observations.values())
report=dict(result='CAPTURED',checks=checks,commands=commands,observations=observations,
    scope='Read-only production-module observer, native/selected neutrality pilots and ordinary power-on input continuations. Timer/camera/player observations retained without forcing guest state. Original MD per-context decision comparison, selected LLE and production replay still needed.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('CAPTURED',checks,flush=True)
