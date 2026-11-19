"""Current Hakuna checkpoint, reusing only the existing nearby Exile continuation."""
import json,subprocess,os
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna778-checkpoint';out.mkdir(exist_ok=True)
cmd=json.loads((ROOT/'build/next755-exile/report.json').read_text())['cases']['md']['command'].copy();cmd[0]=str(ROOT/'dist/installed-preview771/LionKing.exe')
for flag,value in (('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_text('opengl = 0\nscale = 1\n');(out/'resources.ini').write_text((ROOT/'profiles/exile-md.ini').read_text());cmd+=['--save-at','27000',str(out/'entry.state')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=50,creationflags=subprocess.CREATE_NO_WINDOW)
scene=json.loads((out/'scene.json').read_text());assert scene['level']==5 and scene['latched_gameplay']['health']>0
(out/'report.json').write_text(json.dumps(dict(result='PASS',command=cmd,scene=scene['latched_gameplay'],source_sha256={Path(__file__).relative_to(ROOT).as_posix():digest(Path(__file__))}),indent=2)+'\n');print('HAKUNA',scene['latched_gameplay'])
