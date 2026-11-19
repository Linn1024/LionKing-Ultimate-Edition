"""Finish level selection before enabling the independent polled replay hook."""
from pathlib import Path
template=Path(__file__).with_name('check_cant_wait484_route.py')
s=template.read_text().replace('build/cant-wait484-route','build/cant-wait485-route')
anchor="USER32.SetProcessDPIAware();hwnd=None;events=[];last=None;snapshots={};next_entry=None"
seed='''# The polled hook overrides actual reads even during the frontend macro.
# Author a real level2-only checkpoint without that hook, then cold-replay it.
seed=cmd.copy();i=seed.index('--input-polled');del seed[i:i+2]
seed[seed.index('--frames')+1]='1530';seed[seed.index('--hash-at')+1]='1530'
state=out/'entry.state';seed+=['--save-at','1530',str(state)]
for flag,name in (('--dump-window','entry.png'),('--dump-scene','entry-scene.json'),('--wav','entry-audio.wav')):seed[seed.index(flag)+1]=str(out/name)
seed_env={k:v for k,v in env.items() if k!='TLK_SOFT_TREE_LOG'};seed_env['TLK_MD_SOUND_COMMANDS']=str(out/'entry-music.csv');seed_env['TLK_AUDIO_STEMS']=str(out/'entry-stems.csv')
with (out/'entry.log').open('wb') as log:subprocess.run(seed,cwd=ROOT,env=seed_env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
entry_scene=json.loads((out/'entry-scene.json').read_text());assert entry_scene['level']==1 and entry_scene['latched_gameplay']['descriptor']==0x3b9 and entry_scene['latched_gameplay']['health']>0
i=cmd.index('--practice-level');del cmd[i:i+2];cmd+=['--load',str(state)]
'''
assert s.count(anchor)==1;s=s.replace(anchor,seed+anchor)
s=s.replace("if not hwnd:hwnd=window_for(proc.pid)","if not hwnd:hwnd=window_for(proc.pid)\n                if hwnd and row['field']>1700 and row['level']==1 and row['descriptor']==0xc003b9 and not row['health']:\n                    capture_client(hwnd,out/'route-death.png');snapshots['route-death']=row;USER32.PostMessageW(hwnd,0x10,0,0);break")
s=s.replace("music=list(csv.DictReader((out/'music.csv').open()));", "music=list(csv.DictReader((out/'entry-music.csv').open()))+list(csv.DictReader((out/'music.csv').open()));")
s=s.replace("command=cmd,original_entry_field=", "command=cmd,seed_command=seed,original_entry_field=")
s=s.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),template,reference,')
exec(compile(s,str(template),'exec'))
