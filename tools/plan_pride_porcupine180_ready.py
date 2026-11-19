"""Observe the real Options boot's stage-ready field before changing approach timing."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
reference=ROOT/'build/pride-porcupine177-difficulty/report.json';ref=bound(reference);assert ref['result']=='NO_ATTRIBUTED_HIT'
out=ROOT/'build/pride-porcupine180-ready';out.mkdir();cmd=ref['commands']['normal'].copy();cmd[0]=str(base/'player.exe')
prefix_path=ROOT/'build/pride-difficulty-start2/snes/normal/ordinary.tape';frames=prefix_path.stat().st_size//2
cmd[cmd.index('--input')+1]=str(prefix_path);cmd[cmd.index('--frames')+1]=str(frames);cmd[cmd.index('--hash-at')+1]=str(frames)
for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_SOFT_TREE_LOG=str(out/'tree.jsonl'))
with (out/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
assert rc==0
rows=[json.loads(line) for line in (out/'tree.jsonl').read_text().splitlines()]
first=next(r for r in rows if r['descriptor']==0xc00387 and r['level']==0 and r['health']==4)
original=ROOT/'build/pride-reset/fixed4/native/gates/allbugs-aot.ram';old=[line.split() for line in original.read_text().splitlines()]
original_ready=next(int(r[0]) for r in old if int(r[3],16)==4 and int(r[4],16)==64 and int(r[5],16)>=1248)
target=first['field']+(943-original_ready)-1
checks=dict(actual_native_options_persisted=first['difficulty']==1 and first['lives']==2,ordinary_timing_plan_within_final_neutral_tail=frames-400<target<=frames)
paths=[Path(__file__),bp,reference,prefix_path,original]
(out/'report.json').write_text(json.dumps(dict(result='PLANNED' if all(checks.values()) else 'NEEDS_REVIEW',checks=checks,command=cmd,
    options_first_ready=first['field'],original_first_ready=original_ready,target_prefix_fields=target,original_prefix_fields=frames,trim_fields=frames-target,
    scope='Observed current Options stage ownership, planning a controller-only shorter neutral suffix. Matching readiness is not proof of identical enemy state or a porcupine contact.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PLAN',checks,'ready',first['field'],'target prefix',target,'trim',frames-target,flush=True)
