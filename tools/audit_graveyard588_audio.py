"""Inventory actual Graveyard sound callers from the retained level entry, without earlier-level replay."""
import collections,csv,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard516-route/report.json';r=bound(reference)
build=ROOT/'build/cant-wait579/build-report.json';bound(build)
out=ROOT/'build/graveyard588-audio';out.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(build.parent/'player.exe');i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--frames','18840'),('--hash-at','13500,15500,18000,18840'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json')),('--wav',str(out/'audio.wav')),('--sprite-assets',str(ROOT/'build/graveyard529-helper/sprites.assets'))):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_text('opengl = 0\nscale = 1\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\naudio.music.elephant_graveyard = md\n')
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_AUDIO_EVENTS=str(out/'events.csv'),TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv'))
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW)
events=[];counts=collections.Counter()
for row in csv.DictReader((out/'events.csv').open()):
    if int(row['level'],16)!=2 or int(row['descriptor'],16)!=0x3eb:continue
    stack=bytes.fromhex(row['stack']);caller=stack[7]<<16|((int.from_bytes(stack[5:7],'little')+1)&65535)
    row['caller']=hex(caller);events.append(row);counts[(row['event'],hex(caller))]+=1
frames=ROOT/'build/md-next-levels-replay/frames.json';original=ROOT/'build/md-next-levels-replay/commands.csv';levels={x['frame']:x['level'] for x in json.loads(frames.read_text())}
md=[x for x in csv.DictReader(original.open()) if levels.get(int(x['frame']))==2 and int(x['selector']) in (1,2,19)];mdcounts=collections.Counter((x['selector'],x['value'],x['outer_caller']) for x in md)
paths=[Path(__file__),reference,build,frames,original]
(out/'report.json').write_text(json.dumps(dict(result='GRAVEYARD_AUDIO_INVENTORY',command=cmd,native_counts=[dict(event=e,caller=c,count=n) for (e,c),n in counts.items()],md_counts=[dict(selector=s,value=v,caller=c,count=n) for (s,v,c),n in mdcounts.items()],native_events=events,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print('NATIVE',list(counts.items()));print('MD',list(mdcounts.items()),flush=True)
