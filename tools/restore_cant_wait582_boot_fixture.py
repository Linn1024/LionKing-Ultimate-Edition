"""Recreate a volatile practice boot file only when it matches the original recorded digest."""
import json,os,shutil,subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
reference=ROOT/'build/cant-wait573-route-audio/report.json';r=json.loads(reference.read_text())
out=ROOT/'build/cant-wait582-boot-fixture';out.mkdir(exist_ok=True);cmd=r['commands']['seed'].copy()
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(__import__('pathlib').Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(out/name)
cmd[-1]=str(out/'entry.state')
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
boot=out/'tlk_practice_boot.state';target=reference.parent/boot.name
assert digest(boot)==r['artifacts_sha256'][boot.name],(digest(boot),r['artifacts_sha256'][boot.name])
shutil.copy2(target,out/'overwritten.state');shutil.copy2(boot,target)
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_BYTES_RESTORED',reason='Contact checks reused the route config folder, so the launcher rewrote its volatile boot state. Recreating the original direct-select seed restores only exactly matching recorded bytes; route proof and source checks are unchanged.',command=cmd,restored_sha256=digest(target)),indent=2)+'\n');print('RESTORED',digest(target),flush=True)
