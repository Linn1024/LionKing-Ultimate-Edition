"""Short ordinary attack excerpt: audio timing independent of contact timing."""
import csv,json,os,re,subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride-porcupine327/build-report.json';bound(build)
out=ROOT/'build/pride-porcupine328';out.mkdir(exist_ok=True)
ref=json.loads((ROOT/'build/pride-battle320/report.json').read_text());commands={}
labels=['native-old','native-new','md-voice-new','md-voice-lle','md-both-old','md-both-new']
def run(label):
    folder=out/label;folder.mkdir(exist_ok=True);cmd=ref['commands']['md-new'].copy()
    cmd[0]=str(ROOT/('build/pride-battle319/player.exe' if label.endswith('old') else 'build/pride-porcupine327/player.exe'))
    i=cmd.index('--save-at');del cmd[i:i+3]
    cmd[cmd.index('--input-polled')+1]=str(ROOT/'engine/tapes/allbugsF.read.tape')
    cmd[cmd.index('--frames')+1]='2000';cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(1400,1801)))
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    profile='schema = 1\ngame = snes\n'
    if label.startswith('md-'):profile+='audio.effects.world.porcupine = md\n'
    if label.startswith('md-both'):profile+='gameplay.levels.pride_lands.porcupine_attack = md\n'
    (folder/'resources.ini').write_text(profile)
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
    if label.endswith('lle'):cmd+=['--lle']
    commands[label]=cmd
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env.update(SDL_VIDEODRIVER='dummy',TLK_PORCUPINE_VOICE_TRACE=str(folder/'voice.csv'))
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    print(label,rc,flush=True);return label,rc
with ThreadPoolExecutor(max_workers=2) as pool:exits=dict(pool.map(run,labels))
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda label:re.findall(pattern,(out/label/'run.log').read_text())
media=lambda label,name:digest(out/label/name)
voices={label:list(csv.DictReader((out/label/'voice.csv').open())) if (out/label/'voice.csv').exists() else [] for label in labels}
checks=dict(exits=all(v==0 for v in exits.values()),native_guest=len(rows('native-new'))==401 and rows('native-old')==rows('native-new'),native_pcm=media('native-old','audio.wav')==media('native-new','audio.wav'),
    md_voice_guest=rows('native-new')==rows('md-voice-new')==rows('md-voice-lle'),md_voice_aot_lle_pcm=media('md-voice-new','audio.wav')==media('md-voice-lle','audio.wav'),
    md_voice_cue=bool(voices['md-voice-new']) and voices['md-voice-new']==voices['md-voice-lle'] and all(r['counter']=='28' and r['gameplay_md']=='0' for r in voices['md-voice-new']),
    md_gameplay_guest=rows('md-both-old')==rows('md-both-new'),md_gameplay_pcm=media('md-both-old','audio.wav')==media('md-both-new','audio.wav'),md_gameplay_cue=bool(voices['md-both-new']) and all(r['counter']=='28' and r['gameplay_md']=='1' for r in voices['md-both-new']))
paths=[Path(__file__),build,ROOT/'build/pride-battle319/build-report.json',ROOT/'engine/tapes/allbugsF.read.tape']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,voices=voices,commands=commands,scope='Only first ordinary attack excerpt through2000 fields. Native preservation, audio-only AOT/LLE, and selected gameplay source checked. No full All Bugs or other level suites.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
