"""Production compiled/interpreted neutrality for the three attributed hit routes."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
reference=ROOT/'build/pride-porcupine186-polled/report.json';ref=bound(reference);assert ref['result']=='CAPTURED'
proof=ROOT/'build/pride-porcupine187-difficulty/report.json';assert bound(proof)['result']=='PASS'
out=ROOT/'build/pride-porcupine188-modes';out.mkdir();checks={};commands={};pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
for difficulty in ('easy','normal','hard'):
    observed=reference.parent/difficulty
    for mode in ('aot','lle'):
        label=difficulty+'-'+mode;folder=out/label;folder.mkdir();cmd=ref['commands'][difficulty].copy();cmd[0]=str(base/'player.exe')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if mode=='lle':cmd+=['--lle']
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
        with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        commands[label]=cmd;checks[label+'_all900_guest_fields_neutral']=rc==0 and len(rows(folder))==900 and rows(folder)==rows(observed)
        for file in ('window.png','scene.json','audio.wav'):checks[label+'_'+file+'_neutral']=digest(folder/file)==digest(observed/file)
        print(label,'exit',rc,'neutral',checks[label+'_all900_guest_fields_neutral'],flush=True)
checks['binary_exact']=digest(base/'player.exe')==digest(ROOT/'dist/installed-preview139/LionKing.exe')==b['binary_sha256']
paths=[Path(__file__),bp,reference,proof]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='Three current139 actual porcupine hit/protection continuations. All900 sample fields and complete media match the read-only observer in each production execution mode. No old-build saves or guest edits. Original MD comparison separately bound by187.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
