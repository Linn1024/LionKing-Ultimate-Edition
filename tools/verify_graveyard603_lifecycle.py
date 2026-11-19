"""Current bone countdown save/load and actual native pause preserve one delayed sound."""
import csv,hashlib,json,os,re,struct,subprocess,wave
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard597-opening/report.json';r=bound(reference);build=ROOT/'build/graveyard599/build-report.json';bound(build)
out=ROOT/'build/graveyard603-lifecycle';out.mkdir(exist_ok=True);commands={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
def run(name,load=None,end=13820,save=None,point=None,tape=None,raw=False):
    folder=out/name;folder.mkdir(exist_ok=True);cmd=r['commands']['all'].copy();cmd[0]=str(build.parent/'player.exe');i=cmd.index('--save-at');del cmd[i:i+3]
    for flag,value in (('--frames',str(end)),('--hash-at',str(end) if not point else f'{point},{end}'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):
        if flag in ('--config','--resource-profile'):Path(value).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes())
        cmd[cmd.index(flag)+1]=value
    if load:cmd[cmd.index('--load')+1]=str(load)
    if tape:cmd[cmd.index('--input-polled')+1]=str(tape)
    if raw:cmd[cmd.index('--input-polled')]='--input'
    if save:cmd+=['--save-at',str(point),str(save)]
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[name]=cmd;return folder
state=out/'pending.state';full=run('full',save=state,point=13640);loaded=run('loaded',state,tape=reference.parent/'all/pending.polled.tape')
pause=out/'pause.tape';pads=bytearray(13900*2)
for field in (13642,13643,13644,13710,13711,13712):struct.pack_into('<H',pads,field*2,0x1000)
pause.write_bytes(pads);paused=out/'paused.state';pfull=run('pause-full',state,13780,paused,13655,pause,True);pload=run('pause-loaded',paused,13780,tape=pause,raw=True)
def pcm(p):
    with wave.open(str(p),'rb') as f:return f.readframes(f.getnframes())
def hashrow(folder):return re.findall(r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+',(folder/'run.log').read_text())[-1]
def count(folder):return sum(x['selector']=='2' and x['value']=='105' for x in csv.DictReader((folder/'commands.csv').open()))
raw=paused.read_bytes();needle=bytes.fromhex('a28dc5');found=[];start=0
while (at:=raw.find(needle,start))>=0:
    start=at+1;offset=at-0xb817
    if offset>=0 and raw[offset+0xb843:offset+0xb846]==bytes.fromhex('f999c1'):found.append(offset)
assert len(found)==1;ram=raw[found[0]:found[0]+0x20000];w=lambda at:struct.unpack_from('<H',ram,at)[0]
checks=dict(native_pending_countdown=bool(w(0xa89)) and w(0xb813+0x2c)>10,current_resume_pcm=pcm(full/'audio.wav')[-len(pcm(loaded/'audio.wav')):]==pcm(loaded/'audio.wav'),current_guest=hashrow(full)==hashrow(loaded),current_window=ImageChops.difference(Image.open(full/'window.png'),Image.open(loaded/'window.png')).getbbox() is None,delayed_cue_once=count(loaded)==1,pause_resume_pcm=pcm(pfull/'audio.wav')[-len(pcm(pload/'audio.wav')):]==pcm(pload/'audio.wav'),pause_guest=hashrow(pfull)==hashrow(pload),pause_cue_once=count(pfull)==count(pload)==1,pause_window=ImageChops.difference(Image.open(pfull/'window.png'),Image.open(pload/'window.png')).getbbox() is None)
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,saved_pause=w(0xa89),saved_counter=w(0xb813+0x2c),scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
