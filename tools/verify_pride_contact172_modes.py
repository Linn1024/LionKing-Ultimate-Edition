"""Uninstrumented production AOT/LLE parity for all fresh current contact samples."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';build=bound(bp)
capture_path=ROOT/'build/pride-contact170-current/report.json';capture=bound(capture_path);assert capture['result']=='CAPTURED'
comparison=ROOT/'build/pride-contact171-comparison/report.json';assert bound(comparison)['result']=='PASS'
cases=json.loads((capture_path.parent/'snes.json').read_text())['cases'];out=ROOT/'build/pride-contact172-modes';out.mkdir()
checks={};commands={};pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda folder:[r for r in re.findall(pattern,(folder/'run.log').read_text()) if int(r[0])>=2457]
for name,samples in cases.items():
    observed=ROOT/'build/pride-contact167-current/long-roll-chase' if name=='long-roll-chase' else capture_path.parent/name
    for mode in ('aot','lle'):
        label=name+'-'+mode;folder=out/label;folder.mkdir();cmd=capture['commands'].get(name,capture['commands']['repeated-roll-chase']).copy();cmd[0]=str(base/'player.exe')
        frames=2456+len(samples);cmd[cmd.index('--frames')+1]=str(frames);cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(2457,frames+1)))
        cmd[cmd.index('--input')+1]=str(capture_path.parent/(name+'.tape'))
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes((observed/file).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if mode=='lle':cmd+=['--lle']
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
        with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        commands[label]=cmd;checks[label+'_exit_and_every_guest_field_neutral']=rc==0 and len(rows(folder))==len(samples) and rows(folder)==rows(observed)
        for file in ('window.png','scene.json','audio.wav'):checks[label+'_'+file+'_neutral']=digest(folder/file)==digest(observed/file)
        print(label,checks[label+'_exit_and_every_guest_field_neutral'],flush=True)
checks['all1238_samples_per_mode']=sum(map(len,cases.values()))==1238
checks['public_binary_exact']=digest(base/'player.exe')==digest(ROOT/'dist/installed-preview139/LionKing.exe')==build['binary_sha256']
paths=[Path(__file__),bp,capture_path,comparison]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
    scope='All three fresh current139 contact protocols, every1238 sample canonical/fullWRAM hashes and complete media reproduce the read-only observer in production compiled/interpreted modes. Original MD physical/state comparison is separately bound by171. No old-build saves used; no universal combat/AI claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
