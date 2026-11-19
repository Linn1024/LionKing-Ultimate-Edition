"""Author ordinary Easy menu inputs for the final available-MD TAS replay."""
import csv,gzip,json,os,shutil,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
out=ROOT/'build/remaining1024-boot';out.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/remaining1016-client/report.json').read_text())['cases']['direct']['command'].copy()
for flag,n in (('--load',2),('--save-at',3)):
 if flag in cmd:i=cmd.index(flag);del cmd[i:i+n]
cmd[0]=str(ROOT/'dist/installed-preview1014/LionKing.exe')
for flag,value in (('--frames',2200),('--hash-at',2200),('--config',out/'host.ini'),('--resource-profile',out/'resources.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json'),('--input-polled',out/'boot.polled.tape')):cmd[cmd.index(flag)+1]=str(value)
(out/'host.ini').write_text('opengl = 0\nscale = 1\n');shutil.copy2(ROOT/'profiles/available-md.ini',out/'resources.ini');pads=[0]*500
def tap(p,wait):pads.extend([p]*2+[0]*wait)
tap(0x400,20);tap(0x1000,100);tap(0x80,20);tap(0x80,20);tap(0x1000,100);tap(0x1000,500)
(out/'boot.polled.tape').write_bytes(struct.pack('<'+'H'*len(pads),*pads));trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(TLK_SOFT_TREE_LOG=trace.name,TLK_BG_TRACE=str(out/'scenes.csv'))
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
trace.finish();rows=[json.loads(line) for line in gzip.open(out/'tree.jsonl.gz','rt')];scenes=list(csv.DictReader((out/'scenes.csv').open()));start=next((int(r['frame']) for r in scenes if r['stage']=='1' and r['level']=='0' and int(r['descriptor'])==0x387),None);at=next((r for r in rows if r['field']==start),None);last=rows[-1];scene=json.loads((out/'scene.json').read_text());checks=dict(easy=last['difficulty']==0,lives8=last['lives']==8,ordinary_pride=last['descriptor']==0xc00387 and last['health']>0,first_scene_found=at is not None)
if all(checks.values()):
 end=at['poll_index'];(out/'prefix.polled.tape').write_bytes(struct.pack('<'+'H'*end,*pads[:end]))
paths=[Path(__file__),out/'resources.ini',out/'boot.polled.tape']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,command=cmd,first_stage_field=start,first_stage_poll=at and at['poll_index'],last={k:last[k] for k in ('field','difficulty','level','health','lives','poll_index')},gameplay=scene['latched_gameplay'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,'first',start,at and at['poll_index'],scene['latched_gameplay'],flush=True)
