"""Resume one current mid-death music save through retry; no old-save compatibility work."""
import csv,json,os,re,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_audio_state import audio_offset,wav_data
reference=ROOT/'build/graveyard637-death/both/report.json';r=bound(reference);out=ROOT/'build/graveyard639-save';out.mkdir();commands={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for label in ('save','resume'):
    folder=out/label;folder.mkdir();cmd=r['command'].copy()
    for flag,value in (('--hash-at','19800'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):cmd[cmd.index(flag)+1]=value
    (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_bytes((reference.parent/'resources.ini').read_bytes())
    if label=='save':cmd+=['--save-at','19200',str(out/'death.state')]
    else:cmd[cmd.index('--load')+1]=str(out/'death.state');cmd[cmd.index('--input-polled')+1]=str(ROOT/'build/graveyard636-death/both/idle.polled.tape')
    with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    commands[label]=cmd
raw=(out/'death.state').read_bytes();at=audio_offset(raw);actual=wav_data(out/'resume/audio.wav');expected=wav_data(out/'save/audio.wav');pattern=r'frame=19800 frame_sha256=\w+ wram_sha256=\w+'
music=[int(x['value']) for x in csv.DictReader((out/'resume/commands.csv').open()) if x['selector']=='1'];checks=dict(saved_death_hold=struct.unpack_from('<I',raw,at+112)[0]==2,exact_pcm_continuation=bool(actual) and expected[-len(actual):]==actual,guest_continuation=re.findall(pattern,(out/'save/run.log').read_text())==re.findall(pattern,(out/'resume/run.log').read_text()),retry_restarts_level_track=music==[83],living_retry=json.loads((out/'resume/scene.json').read_text())['latched_gameplay']['health']==6)
paths=[Path(__file__),reference,ROOT/'build/graveyard635/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
