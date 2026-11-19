"""Inspect the failed reaction's actual current owner at its entry, without changing game state."""
import hashlib,json,os,re,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait556-animals/report.json';r=bound(reference)
out=ROOT/'build/cant-wait557-reaction-owner';out.mkdir(exist_ok=True);cmd=r['commands']['reaction'].copy()
for flag,value in (('--frames','2084'),('--hash-at','2084'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json')),('--wav',str(out/'audio.wav'))):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_bytes((reference.parent/'reaction/host.ini').read_bytes());(out/'resources.ini').write_bytes((reference.parent/'reaction/resources.ini').read_bytes());state=out/'entry.state';cmd+=['--save-at','2084',str(state)]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
scene=json.loads((out/'scene.json').read_text());raw=state.read_bytes();needle=struct.pack('<HH',*scene['latched_gameplay']['player']);expected=re.findall(r'wram_sha256=([0-9a-f]+)',(out/'run.log').read_text())[-1];found=[];start=0
while (at:=raw.find(needle,start))>=0:
    start=at+1;offset=at-0xb21b
    if offset>=0 and hashlib.sha256(raw[offset:offset+0x20000]).hexdigest()==expected:found.append(offset)
assert len(found)==1;ram=raw[found[0]:found[0]+0x20000];(out/'wram.bin').write_bytes(ram)
w=lambda at:struct.unpack_from('<H',ram,at)[0];a=lambda at:int.from_bytes(ram[at:at+3],'little');rows=[]
for actor in range(0x8000,0xff80,2):
    if a(actor+0x30)!=0xc455ac:continue
    draw=w(actor+12);rows.append(dict(actor=hex(actor),descriptor=hex(a(actor+4)),counter=w(actor+0x2e),draw=hex(draw),position=hex(w(draw+4)),draw_flags=hex(w(draw+8)),draw_pose=hex(a(draw+10))))
paths=[Path(__file__),reference]
(out/'report.json').write_text(json.dumps(dict(result='REACTION_OWNER_INSPECTED',actors=rows,command=cmd,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(rows,flush=True)
