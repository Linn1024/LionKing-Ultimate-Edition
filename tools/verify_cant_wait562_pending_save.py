"""One current pending monkey reaction save; compare resumed sound and play with continuous run."""
import csv,json,os,re,subprocess,wave
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait561-animals/report.json';r=bound(reference)
assert r['result']=='PASS'
out=ROOT/'build/cant-wait562-pending-save';out.mkdir(exist_ok=True);commands={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
def run(name,end,state=None,tape=None,save=None):
    folder=out/name;folder.mkdir(exist_ok=True);cmd=r['commands']['all'].copy()
    for flag,value in (('--frames',str(end)),('--hash-at',str(end)),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):cmd[cmd.index(flag)+1]=value
    for filename in ('host.ini','resources.ini'):(folder/filename).write_bytes((reference.parent/'all'/filename).read_bytes())
    if state:cmd[cmd.index('--load')+1]=str(state)
    if tape:cmd[cmd.index('--input-polled')+1]=str(tape)
    if save:cmd+=['--save-at',str(end),str(save)]
    commands[name]=cmd
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    return folder
state=out/'pending.state';prefix=run('save',2084,save=state)
used=int(re.search(r'tape_words_used=(\d+)',(prefix/'run.log').read_text()).group(1))
suffix=out/'remaining.polled.tape';suffix.write_bytes(Path(commands['save'][commands['save'].index('--input-polled')+1]).read_bytes()[used*2:])
tail=run('load',2130,state,suffix)
def pcm(path):
    with wave.open(str(path),'rb') as f:return f.readframes(f.getnframes())
whole=pcm(reference.parent/'all/audio.wav');a=pcm(prefix/'audio.wav');b=pcm(tail/'audio.wav')
pattern=r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+'
sounds={(x['selector'],x['value']) for x in csv.DictReader((tail/'commands.csv').open())}
checks=dict(pending_voice_not_yet_played=('19','8') not in {(x['selector'],x['value']) for x in csv.DictReader((prefix/'commands.csv').open())},voice_plays_after_load=('19','8') in sounds,prefix_pcm=whole[:len(a)]==a,resumed_pcm=whole[len(a):]==b,final_guest=re.findall(pattern,(tail/'run.log').read_text())==re.findall(pattern,(reference.parent/'all/run.log').read_text()),actual_window=ImageChops.difference(Image.open(tail/'window.png'),Image.open(reference.parent/'all/window.png')).getbbox() is None)
paths=[Path(__file__),reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
assert all(checks.values())
