"""Fresh Options checkpoints then ordinary per-poll approach, without game edits."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
source=ROOT/'build/pride-porcupine183-actual-aligned/report.json';ref=bound(source);assert ref['result']=='NO_ATTRIBUTED_HIT'
observer=ROOT/'build/pride-damage184-observer';bp=observer/'build-report.json';bound(bp)
base=ROOT/'build/pride-hyena-entrance139';bound(base/'build-report.json')
out=ROOT/'build/pride-porcupine186-polled';out.mkdir();commands={};cases={}
original=ROOT/'engine/tapes/allbugsF.read.tape';raw=original.read_bytes();words=struct.unpack('<'+'H'*(len(raw)//2),raw);first=words.index(0x100);assert first==638
tail=out/'approach.polled.tape';tail.write_bytes(raw[first*2:1096*2]+struct.pack('<'+'H'*400,*([0]*400)))
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
for difficulty,spares in [('easy',8),('normal',2),('hard',0)]:
    folder=out/difficulty;folder.mkdir();start=ref['cases'][difficulty]['prefix_fields'];cmd=ref['commands'][difficulty].copy();cmd[0]=str(base/'player.exe')
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
    for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/('seed-'+file))
    state=folder/'current.state';cmd[cmd.index('--frames')+1]=str(start);cmd[cmd.index('--hash-at')+1]=str(start);cmd+=['--save-at',str(start),str(state)]
    with (folder/'seed.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=f,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    assert rc==0,(difficulty,'seed',rc);commands[difficulty+'-seed']=cmd.copy()
    cmd[0]=str(observer/'player.exe');i=cmd.index('--save-at');del cmd[i:i+3];i=cmd.index('--input');cmd[i]='--input-polled';cmd[i+1]=str(tail)
    cmd[cmd.index('--frames')+1]=str(start+900);cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(start+1,start+901)));cmd+=['--load',str(state)]
    for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
    env=dict(clean,TLK_DAMAGE184=str(folder/'damage.csv'),TLK_DAMAGE_FIRST184=str(start+1))
    with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    assert rc==0,(difficulty,'approach',rc);commands[difficulty]=cmd.copy()
    rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader((folder/'damage.csv').open())]
    assert rows[0]['health']==4 and rows[0]['spares']==spares,(difficulty,rows[0])
    drops=[dict(field=b['field'],before=a['health'],after=b['health'],prior=a,current=b,porcupine=a['pending']==4 and a['attacker_descriptor']==0xc58c5c,attack=a['pending']==4 and a['attacker_descriptor']==0xc58c5c and a['attacker_action']==0xc15b87) for a,b in zip(rows,rows[1:]) if b['health']<a['health']]
    cases[difficulty]=dict(initial=rows[0],drops=drops,porcupine_hits=[d for d in drops if d['porcupine']],prefix_fields=start)
    print(difficulty,[(d['field'],d['before'],d['after'],hex(d['prior']['attacker_descriptor']),d['attack']) for d in drops],flush=True)
    (out/'partial.json').write_text(json.dumps(cases,indent=2)+'\n')
checks=dict(real_difficulty_options_and_fresh_checkpoints=True,all_three_have_porcupine_hits=all(r['porcupine_hits'] for r in cases.values()))
paths=[Path(__file__),source,bp,original]
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED' if all(checks.values()) else 'NO_ATTRIBUTED_HIT',checks=checks,cases=cases,commands=commands,
    scope='Fresh ordinary Options boots to observed initialized actor age, current same-build checkpoint as planning aid, then original per-controller-read approach and neutral. No actor/RNG/health/difficulty-memory edits. Not an uninterrupted power-on proof; production replay and original MD comparison separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('CAPTURED' if all(checks.values()) else 'NO_ATTRIBUTED_HIT',checks,flush=True)
