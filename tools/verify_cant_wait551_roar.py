"""One ordinary first-roar segment checks native preservation, MD cue and scene tail lifetime."""
import csv,json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait547-audio/report.json';r=bound(reference)
build=ROOT/'build/cant-wait550/build-report.json';bound(build)
out=ROOT/'build/cant-wait551-roar';out.mkdir(exist_ok=True);commands={};logs={};scenes={};pictures={};events={};music={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,exe,md in [('old',ROOT/'build/graveyard536/player.exe',False),('native',build.parent/'player.exe',False),('md',build.parent/'player.exe',True)]:
    folder=out/name;folder.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(exe)
    for flag,value in (('--frames','2130'),('--hash-at','2130'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav')),('--wav-seconds','12')):cmd[cmd.index(flag)+1]=value
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\naudio.music.cant_wait_to_be_king = md\n'+('audio.effects.simba.roar = md\n' if md else ''))
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[name]=cmd;logs[name]=(folder/'run.log').read_text();scenes[name]=json.loads((folder/'scene.json').read_text());pictures[name]=Image.open(folder/'window.png').convert('RGB');events[name]=list(csv.DictReader((folder/'commands.csv').open()))
checks=dict(native_guest_preserved=re.findall(r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+',logs['old'])==re.findall(r'frame=\d+ frame_sha256=\w+ wram_sha256=\w+',logs['native']),native_audio_preserved=digest(out/'old/audio.wav')==digest(out/'native/audio.wav'),native_windows_preserved=ImageChops.difference(pictures['old'],pictures['native']).getbbox() is None,actual_second_level=all(s['level']==1 and s['latched_gameplay']['descriptor']==0x3b9 for s in scenes.values()),md_roar_command=any(x['selector']=='19' and x['value']=='10' for x in events['md']),native_has_no_md_roar=not any(x['selector']=='19' and x['value']=='10' for x in events['native']),no_repeated_music_restart=sum(x['selector']=='1' and x['value']=='2' for x in events['md'])<=2,md_audio_differs=digest(out/'md/audio.wav')!=digest(out/'native/audio.wav'),gameplay_picture_unchanged=ImageChops.difference(pictures['native'],pictures['md']).getbbox() is None,gameplay_values_unchanged=scenes['native']['latched_gameplay']==scenes['md']['latched_gameplay'])
paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,scope='First ordinary roar in the established second-level route. Native control retains guest/PCM/window; MD choice emits original PCM10 and changes audio while gameplay picture/values match. No whole-level replay. Native-music independence, current audio saves and other effects remain to qualify.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
