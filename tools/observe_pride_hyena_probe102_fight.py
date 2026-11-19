"""Ordinary repeated-hit Normal fight with the unchanged read-only101 observer."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

out=ROOT/'build/pride-hyena-probe102-fight';out.mkdir()
reference=ROOT/'build/pride-menu-enable86/route/report.json';prior=bound(reference)
fight=ROOT/'build/pride-hyena-recovery/snes/report.json';original=bound(fight)
exe=ROOT/'build/pride-hyena-probe101/player.exe';before=digest(exe)
cmd=prior['commands']['menus-aot'].copy();cmd[0]=str(exe)
cmd[cmd.index('--frames')+1]=str(original['cases']['normal']['final']['field'])
tape=ROOT/'build/pride-hyena-normal-repeat-plan/best.polled.tape';cmd[cmd.index('--input-polled')+1]=str(tape)
(out/'host.ini').write_text('opengl = 0\nscale = 2\n')
(out/'resources.ini').write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.hyena_probe_height = md\n')
for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
env.update(SDL_VIDEODRIVER='dummy',TLK_HYENA_PROBE_OBSERVER=str(out/'contexts.csv'),TLK_HYENA_PROBE_TRACE=str(out/'probes.csv'))
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
paths=[Path(__file__),reference,fight,exe,tape];assert digest(exe)==before
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED' if rc==0 else 'FAIL',exit=rc,command=cmd,read_only_wrapper=True,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Normal fight observer exit',rc,flush=True)
