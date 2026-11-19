"""One pickup contact: selected corrected voice and unchanged ordinary presentation."""
import csv,json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait576-continue/report.json';r=bound(reference);build=ROOT/'build/cant-wait579/build-report.json';bound(build)
out=ROOT/'build/cant-wait580-continue-audio';out.mkdir(exist_ok=True);commands={};sounds={};scenes={};images={}
source=Path(r['command'][r['command'].index('--input-polled')+1]);used=int(re.search(r'tape_words_used=(\d+)',(reference.parent/'run.log').read_text()).group(1));tape=out/'contact.polled.tape';tape.write_bytes(source.read_bytes()[used*2:])
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,exe in [('old',ROOT/'build/cant-wait572/player.exe'),('current',build.parent/'player.exe')]:
    folder=out/name;folder.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(exe);i=cmd.index('--save-at');del cmd[i:i+3]
    for flag,value in (('--frames','4110'),('--hash-at','4110'),('--load',str(reference.parent/'entry.state')),('--input-polled',str(tape)),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):cmd[cmd.index(flag)+1]=value
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[name]=cmd;sounds[name]={(x['selector'],x['value']) for x in csv.DictReader((folder/'commands.csv').open())};scenes[name]=json.loads((folder/'scene.json').read_text())['latched_gameplay'];images[name]=Image.open(folder/'window.png')
checks=dict(voice_plays=('19','15') in sounds['current'],old_missing_voice=('19','15') not in sounds['old'],play_preserved=scenes['current']==scenes['old'],actual_window_preserved=ImageChops.difference(images['old'],images['current']).getbbox() is None)
paths=[Path(__file__),reference,ROOT/'build/cant-wait577-continue-contact/report.json',build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
