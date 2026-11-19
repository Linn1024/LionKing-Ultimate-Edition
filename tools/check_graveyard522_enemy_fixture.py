"""One short continuation captures actual later enemies, palette banks and a reusable current save."""
import json,os,re,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard516-route/report.json';r=bound(reference);assert r['result']=='PASS'
out=ROOT/'build/graveyard522-enemies';out.mkdir(exist_ok=True);cmd=r['command'].copy()
i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--frames','14250'),('--hash-at','14250'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
i=cmd.index('--wav');del cmd[i:i+2];i=cmd.index('--wav-seconds');del cmd[i:i+2]
cmd+=['--save-at','14250',str(out/'enemies.state')]
(out/'host.ini').write_bytes((reference.parent/'host.ini').read_bytes());(out/'resources.ini').write_bytes((reference.parent/'resources.ini').read_bytes())
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
scene=json.loads((out/'scene.json').read_text());assert scene['level']==2 and scene['latched_gameplay']['descriptor']==0x3eb and scene['latched_gameplay']['health']>0
inventory=sorted({(hex(p['actor_descriptor']),hex(p['pose']),p['palette']) for p in scene['pieces']})
raw=(out/'enemies.state').read_bytes();locations=[i for i in range(len(raw)) if raw.startswith(b'PPU0',i)];assert len(locations)==1
ppu=locations[0];memory_size=0x10000+0x200+0x200+0x20;regs=struct.unpack_from('<I',raw,ppu+4)[0]-memory_size
# PPU memory is serialized contiguously from cgram through VRAM (ppu.c).
assert 0<regs<1000,regs;cgram=struct.unpack_from('<256H',raw,ppu+8+regs);assert list(cgram[128:144])==scene['obj_palette0']
paths=[Path(__file__),reference,ROOT/'engine/snesrecomp/runner/src/snes/ppu.c']
(out/'report.json').write_text(json.dumps(dict(result='ENEMY_FIXTURE_AUTHORED',command=cmd,scene=scene['latched_gameplay'],inventory=inventory,cgram=list(cgram),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(inventory,flush=True)
