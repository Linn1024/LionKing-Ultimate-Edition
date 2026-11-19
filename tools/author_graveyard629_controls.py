"""Author ordinary Graveyard controller segments from a current complete save; never alter guest memory."""
import hashlib,json,os,re,struct,subprocess,sys
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from windows_json_pipe import JsonPipe
source=ROOT/sys.argv[1];out=ROOT/sys.argv[2];out.mkdir(parents=True);end=int(sys.argv[3]);plan=sys.argv[4]
r=json.loads((source/'report.json').read_text()) if (source/'report.json').exists() else json.loads((source.parent/'report.json').read_text())
cmd=(r['commands']['both'] if 'commands' in r else r['command']).copy();cmd[cmd.index('--load')+1]=str(source/'entry.state')
words=[]
for segment in plan.split(','):
    count,value=segment.split(':');words.extend([int(value,0)]*int(count))
tape=out/'controls.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(words),*words));cmd[cmd.index('--input-polled')+1]=str(tape)
for flag,value in (('--frames',str(end)),('--hash-at',str(end)),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json')),('--wav',str(out/'audio.wav'))):cmd[cmd.index(flag)+1]=value
i=cmd.index('--save-at');cmd[i+1:i+3]=[str(end),str(out/'entry.state')]
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_bytes((ROOT/'build/graveyard623-gameplay/resources.ini').read_bytes())
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SOFT_TREE_LOG=trace.name),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
metadata=trace.finish();last=trace.latest();scene=json.loads((out/'scene.json').read_text());raw=(out/'entry.state').read_bytes();needle=struct.pack('<HH',*scene['latched_gameplay']['player']);expected=re.findall(r'wram_sha256=([0-9a-f]+)',(out/'run.log').read_text())[-1];found=[];at=0
while (at:=raw.find(needle,at))>=0:
    offset=at-0xb21b;at+=1
    if offset>=0 and hashlib.sha256(raw[offset:offset+0x20000]).hexdigest()==expected:found.append(offset)
assert len(found)==1;ram=raw[found[0]:found[0]+0x20000];(out/'wram.bin').write_bytes(ram);w=lambda a:struct.unpack_from('<H',ram,a)[0];p=lambda a:int.from_bytes(ram[a:a+3],'little');actors=[]
for actor in range(0xb293,0xc213,128):
    draw=w(actor+12)
    if 0x8000<=draw<=0xffe8 and w(draw+4)==actor+8:actors.append(dict(actor=hex(actor),descriptor=hex(p(actor+4)),position=[w(actor+8),w(actor+10)],hp=w(actor+0x2a),action=hex(p(actor+0x30)),pose=hex(p(draw+10))))
paths=[Path(__file__),source/'entry.state',ROOT/'build/graveyard621/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='CONTROLS_AUTHORED',command=cmd,scene=scene['latched_gameplay'],last=last,actors=actors,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(scene['latched_gameplay'],actors,flush=True)
