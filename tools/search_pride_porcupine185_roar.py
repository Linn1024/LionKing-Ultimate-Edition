"""Ordinary roar inputs to avoid an earlier lizard and reach the porcupine."""
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
reference=ROOT/'build/pride-porcupine177-difficulty/report.json';ref=bound(reference);assert ref['result']=='NO_ATTRIBUTED_HIT'
observer=ROOT/'build/pride-damage184-observer';bp=observer/'build-report.json';bound(bp)
out=ROOT/'build/pride-porcupine185-roar';out.mkdir();base_cmd=ref['commands']['normal'];original_tape=Path(base_cmd[base_cmd.index('--input')+1]);raw=original_tape.read_bytes();pads=list(struct.unpack('<'+'H'*(len(raw)//2),raw));start=ref['cases']['normal']['prefix_fields']
commands={};cases={};checks={};pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
for name,lead in [('pilot',None),('roar270',270),('roar285',285),('roar295',295),('roar303',303)]:
    folder=out/name;folder.mkdir();inputs=pads.copy()
    if lead is not None:
        for i in range(start+lead,start+lead+20):inputs[i]|=0x80
    tape=folder/'ordinary.tape';tape.write_bytes(struct.pack('<'+'H'*len(inputs),*inputs))
    cmd=base_cmd.copy();cmd[0]=str(observer/'player.exe');cmd[cmd.index('--input')+1]=str(tape)
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
    for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_DAMAGE184=str(folder/'damage.csv'),TLK_DAMAGE_FIRST184=str(start))
    with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    assert rc==0,(name,rc);commands[name]=cmd
    if name=='pilot':
        baseline=reference.parent/'normal'
        checks['pilot_all859_guest_fields_neutral']=len(re.findall(pattern,(folder/'run.log').read_text()))==859 and re.findall(pattern,(folder/'run.log').read_text())==re.findall(pattern,(baseline/'run.log').read_text())
        checks['pilot_whole_pcm_neutral']=digest(folder/'audio.wav')==digest(baseline/'audio.wav')
        assert all(checks.values()),checks
    rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader((folder/'damage.csv').open())]
    hits=[dict(field=b['field'],before=a['health'],after=b['health'],previous=a,current=b,porcupine=a['pending']==4 and a['attacker_descriptor']==0xc58c5c,attack=a['pending']==4 and a['attacker_descriptor']==0xc58c5c and a['attacker_action']==0xc15b87) for a,b in zip(rows,rows[1:]) if b['health']<a['health']]
    cases[name]=dict(hits=hits,porcupine_hits=[r for r in hits if r['porcupine']])
    print(name,'hits',[(r['field'],r['before'],r['after'],hex(r['previous']['attacker_descriptor']),r['attack']) for r in hits],flush=True)
    (out/'partial.json').write_text(json.dumps(cases,indent=2)+'\n')
    if name!='pilot' and cases[name]['porcupine_hits']:break
paths=[Path(__file__),reference,bp,original_tape]
(out/'report.json').write_text(json.dumps(dict(result='CANDIDATE_FOUND' if any(r['porcupine_hits'] for r in cases.values()) else 'NO_PORCUPINE_HIT',checks=checks,commands=commands,cases=cases,
    scope='Normal difficulty ordinary Options/controller inputs with an added roar pulse; no guest state edits. Pilot full-WRAM/picture/PCM neutral. Attributed candidate hits need exact production/LLE and all-difficulty follow-up.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('CANDIDATE_FOUND' if any(r['porcupine_hits'] for r in cases.values()) else 'NO_PORCUPINE_HIT',checks,flush=True)
