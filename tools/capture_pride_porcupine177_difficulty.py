"""Ordinary Options boots and an attributed porcupine approach in current native behavior."""
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';bound(bp)
observer=ROOT/'build/pride-contact166-observer';op=observer/'build-report.json';bound(op)
source=ROOT/'build/pride-difficulty-start2/snes/report.json';assert bound(source)['result']=='CAPTURED'
reference=ROOT/'build/pride-reset/fixed4/native/gates/allbugs-aot.ram'
baseline=[line.split() for line in reference.read_text().splitlines()]
# The retained original tracked log records the held $4218 pad at each field.
# Reuse only the first ordinary approach, then neutral; this is a controller
# experiment, not an assertion of identical enemy phases after a different boot.
approach=[int(row[-1],16) for row in baseline if 943<=int(row[0])<=1400]
assert len(approach)==458 and approach[0]==0x100
out=ROOT/'build/pride-porcupine177-difficulty';out.mkdir();cases={};commands={};paths=[Path(__file__),bp,op,source,reference]
template=bound(base/'boundary159/report.json')['commands']['native']
for difficulty,spares in [('easy',8),('normal',2),('hard',0)]:
    folder=out/difficulty;folder.mkdir();prefix_path=source.parent/difficulty/'ordinary.tape';prefix=prefix_path.read_bytes();start=len(prefix)//2
    pads=list(struct.unpack('<'+'H'*start,prefix))+approach+[0]*400;tape=folder/'ordinary.tape';tape.write_bytes(struct.pack('<'+'H'*len(pads),*pads))
    cmd=template.copy();cmd[0]=str(observer/'player.exe');i=cmd.index('--input-polled');cmd[i]='--input';cmd[i+1]=str(tape)
    cmd[cmd.index('--frames')+1]=str(len(pads));cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(start,len(pads)+1)))
    (folder/'resources.ini').write_text('schema = 1\ngame = snes\n');(folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_CONTACT_RAM166=str(folder/'samples.bin'),TLK_CONTACT_FIRST166=str(start))
    with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    assert rc==0,(difficulty,rc);commands[difficulty]=cmd;rows=[]
    with (folder/'samples.bin').open('rb') as f:
        while header:=f.read(16):
            magic,field,pad,size=struct.unpack('<4I',header);assert magic==0x4b4c5443 and size==0x20000
            ram=f.read(size);assert len(ram)==size;w=lambda at:struct.unpack_from('<H',ram,at)[0]
            attacker=int.from_bytes(ram[0xb237:0xb23a],'little');at=attacker&65535;valid=attacker>>16==0x7e and 0xb293<=at<0xc213 and (at-0xb213)%128==0
            rows.append(dict(field=field,pad=pad,health=w(0x2004),spares=w(0x1ffaa),player=[w(0xb21b),w(0xb21d)],immunity=ram[0xb259],player_action=int.from_bytes(ram[0xb243:0xb246],'little'),pending=ram[0xb256]&4,attacker=attacker,attacker_descriptor=int.from_bytes(ram[at+4:at+7],'little') if valid else 0,attacker_action=int.from_bytes(ram[at+0x30:at+0x33],'little') if valid else 0))
    assert rows and rows[0]['health']==4 and rows[0]['spares']==spares,(difficulty,rows[0])
    drops=[]
    for a,b in zip(rows,rows[1:]):
        if b['health']<a['health']:drops.append(dict(field=b['field'],before=a['health'],after=b['health'],prior=a,current=b,porcupine=a['pending']==4 and a['attacker_descriptor']==0xc58c5c and a['attacker_action']==0xc15b87))
    cases[difficulty]=dict(initial=rows[0],drops=drops,porcupine_hits=[r for r in drops if r['porcupine']],prefix_fields=start)
    (folder/'frames.json').write_text(json.dumps(rows,indent=2)+'\n');paths.append(prefix_path)
    print(difficulty,'drops',[(r['field'],r['before'],r['after'],r['porcupine'],hex(r['prior']['attacker_descriptor'])) for r in drops],flush=True)
    (out/'partial.json').write_text(json.dumps(cases,indent=2)+'\n')
checks=dict(ordinary_options_and_source_lives_confirmed=True,all_three_have_attributed_porcupine_hits=all(r['porcupine_hits'] for r in cases.values()))
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED' if all(checks.values()) else 'NO_ATTRIBUTED_HIT',checks=checks,cases=cases,commands=commands,
    scope='Fresh real Options/controller boot, root SNES current139 guest instructions, ordinary approach derived from original held-pad log then neutral. Full RAM after each field; pending reaction/attacker descriptor/action required for attribution. Different source histories not treated as same hit time. Observer neutrality and original MD comparison separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('CAPTURED' if all(checks.values()) else 'NO_ATTRIBUTED_HIT',checks,flush=True)
