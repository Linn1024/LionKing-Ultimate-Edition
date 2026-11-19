"""Ordinary inputs at the nearby Scar encounter; no actor/health edits."""
import json,os,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/remaining1010-combat';out.mkdir(exist_ok=True);base=json.loads((ROOT/'build/remaining1009-scar/report.json').read_text())['cases']['md']['command'];cases={}
def enemies(path,frame,strip=True):
 p=path
 if strip:p=path.with_suffix('.native');native_fixture(path,p,frame)
 data=p.read_bytes();at=data.find(bytes.fromhex('4905c0'))-0xdf;assert at>=0 and data[at+0x1ff9e:at+0x1ffa0]==b'\x09\0';ram=data[at:at+0x20000];word=lambda p:int.from_bytes(ram[p:p+2],'little');ptr=lambda p:int.from_bytes(ram[p:p+3],'little');return [dict(actor=hex(a),descriptor=hex(ptr(a+4)),x=word(a+8),y=word(a+10),health=word(a+0x2a),action=hex(ptr(a+0x30))) for a in range(0xb293,0xc213,128) if ptr(a+4) in (0xc585e8,0xc585f4,0xc58600)]
initial=enemies(Path(base[base.index('--load')+1]),57000,False)
for name,pads in [('slash',[0x4000 if (i//10)%2==0 else 0 for i in range(300)]),('jump-slash',[0xc000 if i%50<20 else 0x4000 if i%50<30 else 0 for i in range(300)]),('left-slash',[0x4200 if i<30 else 0x4000 if (i//10)%2==0 else 0 for i in range(300)])]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy()
 for flag,value in (('--frames',57200),('--hash-at',57200),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--input-polled',folder/'input.polled.tape')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ngameplay.levels.pride_rock.scar_bounds = md\n');(folder/'input.polled.tape').write_bytes(struct.pack('<'+'H'*len(pads),*pads));cmd+=['--save-at','57200',str(folder/'end.state')]
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))},stdout=log,stderr=subprocess.STDOUT,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
 scene=json.loads((folder/'scene.json').read_text());enemy=enemies(folder/'end.state',57200);cases[name]=dict(command=cmd,gameplay=scene['latched_gameplay'],enemies=enemy);print(name,scene['latched_gameplay'],enemy,flush=True)
checks=dict(real_scar_entry=bool(initial),ordinary_surviving_attack=any(r['gameplay']['health']>0 and any(e['health']<next((a['health'] for a in initial if a['actor']==e['actor']),0) for e in r['enemies']) for r in cases.values()))
paths=[Path(__file__),ROOT/'build/remaining1009-scar/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,initial=initial,cases=cases,scope='Local ordinary attack feasibility; not a complete selected-Scar walkthrough.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
