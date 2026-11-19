"""Inventory actual second-level sound calls from the existing level-only entry and original MD evidence."""
import collections,csv,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/cant-wait485-route/report.json';r=bound(reference)
build=ROOT/'build/graveyard536/build-report.json';bound(build)
out=ROOT/'build/cant-wait547-audio';out.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,value in (('--frames','10000'),('--hash-at','1800,7000,10000'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json')),('--wav',str(out/'audio.wav'))):cmd[cmd.index(flag)+1]=value
cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/graveyard529-helper/sprites.assets')
(out/'host.ini').write_text('opengl = 0\nscale = 1\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\naudio.music.cant_wait_to_be_king = md\n')
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_AUDIO_EVENTS=str(out/'events.csv'),TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv'))
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
events=[];counts=collections.Counter()
for row in csv.DictReader((out/'events.csv').open()):
    if int(row['level'],16)!=1 or int(row['descriptor'],16)!=0x3b9:continue
    stack=bytes.fromhex(row['stack']);caller=stack[7]<<16|((int.from_bytes(stack[5:7],'little')+1)&65535)
    row['caller']=hex(caller);events.append(row);counts[(row['event'],hex(caller),row['actor'])]+=1
frames=ROOT/'build/md-next-levels-replay/frames.json';original=ROOT/'build/md-next-levels-replay/commands.csv';levels={x['frame']:x['level'] for x in json.loads(frames.read_text())}
md=[x for x in csv.DictReader(original.open()) if levels.get(int(x['frame']))==1 and int(x['selector']) in (1,2,19)]
mdcounts=collections.Counter((x['selector'],x['value'],x['outer_caller']) for x in md)
scene=json.loads((out/'scene.json').read_text());paths=[Path(__file__),reference,build,frames,original]
(out/'report.json').write_text(json.dumps(dict(result='SECOND_LEVEL_AUDIO_INVENTORY',command=cmd,native_counts=[dict(event=e,caller=c,actor=a,count=n) for (e,c,a),n in counts.items()],md_counts=[dict(selector=s,value=v,caller=c,count=n) for (s,v,c),n in mdcounts.items()],native_events=events,final_scene=scene['latched_gameplay'],scope='Existing second-level save and correctly sliced controller tape; no earlier-level replay or game modifications. Native scene sound calls and retained original MD commands; this is an inventory, not sound equivalence.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print('NATIVE',list(counts.items()));print('MD',list(mdcounts.items()),flush=True)
