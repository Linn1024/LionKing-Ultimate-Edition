"""Ordinary controller branches at Return's first MD-contact encounter; no game-state cheats."""
import json,os,struct,subprocess,re
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/later914-combat';out.mkdir(exist_ok=True);base=json.loads((ROOT/'build/later912-contacts/report.json').read_text())['cases']['8-md']['command'].copy();env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};cases={}
def actors(path,frame):
 p=path.with_suffix('.native');native_fixture(path,p,frame);data=p.read_bytes();needle=bytes.fromhex('1705c0');start=0;positions=[]
 while (at:=data.find(needle,start))>=0:
  start=at+1;offset=at-0xdf
  if offset>=0 and offset+0x20000<=len(data) and data[offset+0x1ff9e:offset+0x1ffa0]==b'\x08\0':positions.append(offset)
 assert len(positions)==1,positions;ram=data[positions[0]:positions[0]+0x20000];word=lambda p:int.from_bytes(ram[p:p+2],'little');pointer=lambda p:int.from_bytes(ram[p:p+3],'little');found=[]
 for a in range(0xb293,0xc213,128):
  if pointer(a+4)!=0xc58ecc:continue
  draw=word(a+12);found.append(dict(actor=hex(a),x=word(a+8),y=word(a+10),action=hex(pointer(a+0x30)),counter_2a=word(a+0x2a),draw=hex(draw),draw_valid=0x8000<=draw<=0xffe8 and word(draw+4)==a+8,pose=hex(pointer(draw+10)) if 0x8000<=draw<=0xffe8 else None))
 return p,found
def run(name,start,end,load=None,pads=None):
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy()
 for flag,value in (('--frames',end),('--hash-at',end),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 if load:cmd[cmd.index('--load')+1]=str(load)
 if pads is not None:(folder/'input.polled.tape').write_bytes(struct.pack('<'+'H'*len(pads),*pads));cmd[cmd.index('--input-polled')+1]=str(folder/'input.polled.tape')
 cmd+=['--save-at',str(end),str(folder/'current.state')];(folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ngameplay.levels.adult_hyenas.bounds = md\n')
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
 state,enemy=actors(folder/'current.state',end);scene=json.loads((folder/'scene.json').read_text());record=dict(command=cmd,gameplay=scene['latched_gameplay'],enemies=enemy,native_state=str(state));cases[name]=record;print(name,record['gameplay'],enemy,flush=True);return record
entry=run('entry',52000,52120);x=entry['gameplay']['player'][0];enemy=min((a for a in entry['enemies'] if a['draw_valid']),key=lambda a:abs(a['x']-x));direction=0x100 if enemy['x']>=x else 0x200
run('slash',52120,52620,Path(entry['native_state']),[0x4000 if (i//10)%2==0 else 0 for i in range(600)])
checks=dict(ordinary_inputs_only=True,md_contacts_selected=True,surviving_combat=any(r['gameplay']['health']>0 for k,r in cases.items() if k!='entry'),enemy_reacted=any(any(a['counter_2a']<enemy['counter_2a'] for a in r['enemies']) for k,r in cases.items() if k!='entry'))
paths=[Path(__file__),ROOT/'build/later910/build-report.json',ROOT/'build/later912-contacts/report.json']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
