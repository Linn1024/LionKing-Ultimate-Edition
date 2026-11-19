"""Inventory the actual native Hakuna route from the current nearby checkpoint."""
import json,os,re,subprocess
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
out=ROOT/'build/hakuna781-native';out.mkdir(exist_ok=True)
entry=ROOT/'build/hakuna778-checkpoint'
native_fixture(entry/'entry.state',out/'entry.native.state',27000)
used=int(re.search(r'tape_words_used=(\d+)',(entry/'run.log').read_text())[1])
(out/'after27000.polled.tape').write_bytes((ROOT/'build/next755-exile/after24500.polled.tape').read_bytes()[used*2:])
cmd=json.loads((ROOT/'build/next755-exile/report.json').read_text())['cases']['md']['command'].copy()
cmd[0]=str(ROOT/'build/hakuna779-observer/player.exe')
for flag,value in (('--config',out/'host.ini'),('--resource-profile',entry/'resources.ini'),('--load',out/'entry.native.state'),('--input-polled',out/'after27000.polled.tape'),('--frames','40000'),('--hash-at','40000'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
(out/'host.ini').write_text('opengl = 0\nscale = 1\n')
cmd+=['--save-at','38000',str(out/'38000.state')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SPRITE_OBJECTS']=str(out/'poses.csv')
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=150,creationflags=subprocess.CREATE_NO_WINDOW)
s=json.loads((out/'scene.json').read_text())
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',command=cmd,level=s['level'],gameplay=s['latched_gameplay']),indent=2)+'\n');print(s['level'],s['latched_gameplay'])
