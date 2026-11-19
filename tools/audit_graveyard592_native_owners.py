"""Author connected Graveyard action checkpoints and verify full native RAM before reading owners."""
import hashlib,json,os,re,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard588-audio/report.json';r=bound(reference)
out=ROOT/'build/graveyard592-native-owners';out.mkdir(exist_ok=True);base=r['command'];state=Path(base[base.index('--load')+1]);tape=Path(base[base.index('--input-polled')+1]);cases=[]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
for point in (13633,14248,15280,16410):
    folder=out/str(point);folder.mkdir(exist_ok=True);cmd=base.copy()
    for flag,value in (('--load',str(state)),('--input-polled',str(tape)),('--frames',str(point)),('--hash-at',str(point)),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):
        if flag in ('--config','--resource-profile'):Path(value).write_bytes(Path(base[base.index(flag)+1]).read_bytes())
        cmd[cmd.index(flag)+1]=value
    state=folder/'entry.state';cmd+=['--save-at',str(point),str(state)]
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    log=(folder/'run.log').read_text();used=int(re.search(r'tape_words_used=(\d+)',log).group(1));remaining=tape.read_bytes()[used*2:];tape=folder/'remaining.polled.tape';tape.write_bytes(remaining)
    scene=json.loads((folder/'scene.json').read_text());raw=state.read_bytes();needle=struct.pack('<HH',*scene['latched_gameplay']['player']);expected=re.findall(r'wram_sha256=([0-9a-f]+)',log)[-1];found=[];start=0
    while (at:=raw.find(needle,start))>=0:
        start=at+1;offset=at-0xb21b
        if offset>=0 and hashlib.sha256(raw[offset:offset+0x20000]).hexdigest()==expected:found.append(offset)
    assert len(found)==1;ram=raw[found[0]:found[0]+0x20000];(folder/'wram.bin').write_bytes(ram);w=lambda at:struct.unpack_from('<H',ram,at)[0];a=lambda at:int.from_bytes(ram[at:at+3],'little');actors=[]
    for actor in range(0x8000,0xff80):
        draw=w(actor+12)
        if not 0x8000<=draw<=0xffe8 or w(draw+4)!=actor+8 or not 0xc50000<=a(actor+4)<0xc60000:continue
        actors.append(dict(actor=hex(actor),descriptor=hex(a(actor+4)),action=hex(a(actor+0x30)),counter=w(actor+0x2c),draw=hex(draw),pose=hex(a(draw+10)),flags=hex(w(draw+8))))
    cases.append(dict(field=point,command=cmd,actors=actors));print(point,[(x['actor'],x['descriptor'],x['action'],x['counter']) for x in actors],flush=True)
paths=[Path(__file__),reference]
(out/'report.json').write_text(json.dumps(dict(result='NATIVE_OWNERS_AND_CHECKPOINTS',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
