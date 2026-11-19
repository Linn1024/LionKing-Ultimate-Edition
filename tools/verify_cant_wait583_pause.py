"""Pause during a pending monkey reaction, save paused, then resume the same sound once."""
import csv,hashlib,json,os,re,struct,subprocess,wave
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait575-current-save/report.json';r=bound(reference);build=ROOT/'build/cant-wait579/build-report.json';bound(build)
out=ROOT/'build/cant-wait583-pause';out.mkdir(exist_ok=True);tape=out/'pause.tape';pads=bytearray(2200*2)
for field in (2085,2086,2087,2110,2111,2112):struct.pack_into('<H',pads,field*2,0x1000)
tape.write_bytes(pads);commands={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
state=out/'paused.state'
def run(name,load,end,save=False):
    folder=out/name;folder.mkdir(exist_ok=True);cmd=r['commands']['load'].copy();cmd[0]=str(build.parent/'player.exe');i=cmd.index('--input-polled');del cmd[i:i+2];cmd+=['--input',str(tape)]
    for flag,value in (('--load',str(load)),('--frames',str(end)),('--hash-at',str(end)),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):
        if flag in ('--config','--resource-profile'):Path(value).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes())
        cmd[cmd.index(flag)+1]=value
    if save:cmd+=['--save-at','2095',str(state)]
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[name]=cmd;return folder
full=run('full',reference.parent/'pending.state',2150,True);loaded=run('loaded',state,2150)
def pcm(p):
    with wave.open(str(p),'rb') as f:return f.readframes(f.getnframes())
a=pcm(full/'audio.wav');b=pcm(loaded/'audio.wav');raw=state.read_bytes();native=json.loads((full/'scene.json').read_text())
# Locate the serialized native actor layout without depending on envelope offsets.
needle=bytes.fromhex('908bc5');offsets=[];start=0
while (at:=raw.find(needle,start))>=0:
    start=at+1;offset=at-(0xb493+4)
    if offset>=0 and raw[offset+0xb493+0x30:offset+0xb493+0x33]==bytes.fromhex('ac55c4'):offsets.append(offset)
assert len(offsets)==1;ram=raw[offsets[0]:offsets[0]+0x20000];w=lambda at:struct.unpack_from('<H',ram,at)[0]
calls=lambda folder:sum(x['selector']=='19' and x['value']=='8' for x in csv.DictReader((folder/'commands.csv').open()))
checks=dict(saved_actually_paused=bool(w(0xa89)),reaction_wait_preserved=w(0xb493+0x2e)>=15,one_reaction_after_resume=calls(full)==calls(loaded)==1,resumed_pcm_exact=bool(b) and a[-len(b):]==b,window_matches=ImageChops.difference(Image.open(full/'window.png'),Image.open(loaded/'window.png')).getbbox() is None)
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,pause_word=w(0xa89),pending_counter=w(0xb493+0x2e),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
