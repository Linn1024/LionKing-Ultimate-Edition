"""Ordinary Down inputs to avoid the automatic ledge pull near the boundary."""
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
base=ROOT/'build/pride-hyena-entrance139';reference=base/'fights140/report.json';ref=bound(reference)
observer=ROOT/'build/pride-hyena-entrance149-observer';bp=observer/'build-report.json';bound(bp)
plan=ROOT/'build/pride-hyena-entrance145-plan/report.json';p=bound(plan);assert p['result']=='PLANNED'
out=ROOT/'build/pride-hyena-entrance157-drop';out.mkdir();checks={};commands={};observations={};paths=[Path(__file__),reference,bp,plan]
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
# Recheck completed150 pilot bytes directly; no dependency on its still-running
# later route experiments or unfinished report.
for selected,label in [(False,'pilot-native'),(True,'pilot-md')]:
    pilot=ROOT/'build/pride-hyena-entrance150-boundary'/label
    control=reference.parent/('entrance-aot' if selected else 'native')
    checks[label+'_all4320_guest_neutral']=len(hashes(pilot))==4320 and hashes(pilot)==hashes(control)
    checks[label+'_whole_pcm_neutral']=digest(pilot/'audio.wav')==digest(control/'audio.wav')
    paths += [pilot/'run.log',pilot/'audio.wav',pilot/'contexts.csv']
assert all(checks.values()),checks
normal=Path(ref['commands']['native'][ref['commands']['native'].index('--input-polled')+1]);prefix=normal.read_bytes()[:p['polls']*2]
for name,tail in [('down80',[0x400]*80+[0]*420),('leftdown40',[0x600]*40+[0]*460)]:
    tape=out/(name+'.polled.tape');tape.write_bytes(prefix+struct.pack('<'+'H'*len(tail),*tail))
    for selected,label in [(False,'snes'),(True,'md')]:
        folder=out/(name+'-'+label);folder.mkdir();cmd=ref['commands']['entrance-aot' if selected else 'native'].copy();cmd[0]=str(observer/'player.exe')
        cmd[cmd.index('--frames')+1]='4194';cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(1,4195)));cmd[cmd.index('--input-polled')+1]=str(tape)
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_ENTRANCE_CONTEXT149=str(folder/'contexts.csv'))
        with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        assert rc==0,(name,label,rc)
        key=name+'-'+label;commands[key]=cmd;observations[key]=list(csv.DictReader((folder/'contexts.csv').open()))
        checks[key+'_exit_and4194_fields']=len(hashes(folder))==4194
        print(key,'contexts',len(observations[key]),'last',observations[key][-1] if observations[key] else None,flush=True)
    a={int(r['field']):r for r in observations[name+'-snes']};b={int(r['field']):r for r in observations[name+'-md']}
    differences=[dict(field=f,snes=a[f],md=b[f]) for f in sorted(a.keys()&b.keys()) if a[f]['timer']!=b[f]['timer']]
    (out/(name+'-differences.json')).write_text(json.dumps(differences,indent=2)+'\n');print(name,'timer differences',len(differences),differences[:1],flush=True)
    if differences:break
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED',checks=checks,commands=commands,observations=observations,
    scope='Read-only observer with explicitly rechecked production neutrality pilots. Fresh ordinary power-on tapes add Down or Left+Down near the observed entrance; no guest edits. A timer difference is an observation requiring original-decision and production/LLE follow-up, not whole-AI proof.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('CAPTURED',checks,flush=True)
