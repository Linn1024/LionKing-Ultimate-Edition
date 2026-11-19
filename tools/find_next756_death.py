"""Author an ordinary neutral-input Exile health-death fixture from a nearby save."""
import json,os,subprocess,struct,gzip
from audit_scenes import ROOT
from windows_json_pipe import JsonPipe
from next_level_checkpoint import native_fixture
out=ROOT/'build/next756-death';out.mkdir(exist_ok=True);base=json.loads((ROOT/'build/next752-route/report.json').read_text())['command'];cmd=base.copy();cmd[0]=str(ROOT/'build/next754/player.exe')
i=cmd.index('--save-at');del cmd[i:i+3]
state=native_fixture(ROOT/'build/next752-route/exile.state',out/'entry.native.state')
for flag,value in (('--load',str(state)),('--input-polled',str(out/'neutral.polled.tape')),('--frames','26500'),('--hash-at','26500'),('--resource-profile',str(out/'resources.ini')),('--config',str(out/'host.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
(out/'neutral.polled.tape').write_bytes(bytes(4000));(out/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text());(out/'host.ini').write_text('opengl = 0\nscale = 1\n');trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
with (out/'run.log').open('wb') as log:
 try:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
 finally:trace.finish()
rows=[json.loads(x) for x in gzip.open(out/'tree.jsonl.gz','rt')];zero=[r for r in rows if r.get('health')==0 and r.get('level')==4 and r['field']>=24500];scene=json.loads((out/'scene.json').read_text());result=dict(result='OBSERVED',command=cmd,first_zero=zero[0]['field'] if zero else None,last=rows[-1],death=scene['graveyard_death']);(out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print('DEATH candidate',result['first_zero'],scene['graveyard_death'])
