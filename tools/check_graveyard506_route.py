"""Current direct-selected Graveyard route; no earlier-level replay or guest edits."""
import csv,json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/graveyard505-entry/report.json';r=bound(reference)
build=ROOT/'build/graveyard503/build-report.json';bound(build)
out=ROOT/'build/graveyard506-route';out.mkdir(exist_ok=True)
native=ROOT/'build/cant-wait-native/aot/route.ram';rows=[x.split() for x in native.read_text().splitlines()]
entry=next(i for i,x in enumerate(rows) if int(x[6],16)==2 and int(x[4],16)==1008 and int(x[5],16)==336 and int(x[3],16)>0)
used=sum(x[1]=='0' for x in rows[:entry]);assert used==12162
source=ROOT/'engine/tapes/allbugsF.read.tape';tape=out/'graveyard.polled.tape';tape.write_bytes(source.read_bytes()[used*2:])
seed=r['command'].copy()
for flag,value in (('--frames','1505'),('--hash-at','1505'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'entry.png')),('--dump-scene',str(out/'entry-scene.json'))):seed[seed.index(flag)+1]=value
seed[seed.index('--save-at')+2]=str(out/'entry.state');seed[seed.index('--save-at')+1]='1505'
(out/'host.ini').write_bytes((reference.parent/'host.ini').read_bytes());(out/'resources.ini').write_bytes((reference.parent/'resources.ini').read_bytes())
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
seed_env=dict(env,TLK_MD_SOUND_COMMANDS=str(out/'entry-music.csv'))
with (out/'entry.log').open('wb') as log:subprocess.run(seed,cwd=ROOT,env=seed_env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
scene=json.loads((out/'entry-scene.json').read_text());assert scene['level']==2 and scene['latched_gameplay']['descriptor']==0x3eb and scene['latched_gameplay']['player']==[1008,336] and scene['latched_gameplay']['health']>0
cmd=seed.copy()
for flag,count in (('--save-at',3),('--practice-level',2)):
    i=cmd.index(flag);del cmd[i:i+count]
cmd+=['--load',str(out/'entry.state'),'--input-polled',str(tape),'--wav',str(out/'audio.wav'),'--wav-seconds','1']
for flag,value in (('--frames','9000'),('--hash-at','1800,4000,7000'),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
trace=JsonPipe(out/'tree.jsonl.gz');env.update(TLK_SOFT_TREE_LOG=trace.name,TLK_MD_SOUND_COMMANDS=str(out/'music.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv'))
USER32.SetProcessDPIAware();hwnd=None;events=[];last=None;snapshots={};next_entry=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+100
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row:
                key=tuple(row[k] for k in ('level','descriptor','health','lives'))
                if key!=last:events.append({k:row[k] for k in ('field','level','descriptor','health','lives','poll_index','macro_index','macro_length')});last=key
                if not hwnd:hwnd=window_for(proc.pid)
                if hwnd and row['field']>1600 and row['level']==2 and row['descriptor']==0xc003eb and not row['health']:
                    capture_client(hwnd,out/'route-death.png');snapshots['route-death']=row;USER32.PostMessageW(hwnd,0x10,0,0);break
                if hwnd and row['level']==2 and row['descriptor']==0xc003eb and row['health']>0:
                    for name,field in (('opening',2000),('middle',4000),('late',6500)):
                        if name not in snapshots and row['field']>=field:capture_client(hwnd,out/(name+'.png'));snapshots[name]=row
                if row['level']==3 and row['descriptor']==0xc0041d and row['health']>0:
                    if next_entry is None:next_entry=row['field']
                    if hwnd and row['field']>=next_entry+180:capture_client(hwnd,out/'stampede.png');snapshots['stampede']=row;USER32.PostMessageW(hwnd,0x10,0,0);break
            time.sleep(.008)
        proc.wait(timeout=15)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish()
music=list(csv.DictReader((out/'entry-music.csv').open()))+list(csv.DictReader((out/'music.csv').open()));stems=list(csv.DictReader((out/'stems.csv').open()))
checks=dict(exit=proc.returncode==0,direct_level_select=True,graveyard_entered=any(e['level']==2 and e['descriptor']==0xc003eb for e in events),reached_stampede='stampede' in snapshots,md_theme_command=any(c['selector']=='1' and c['value']=='83' for c in music),md_audio_rendered=any(int(v['md_peak'])>500 for v in stems),actual_windows=len(snapshots)>=3)
paths=[Path(__file__),reference,build,native,source]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'ROUTE_INCOMPLETE',checks=checks,command=cmd,seed_command=seed,original_entry_field=entry+1,original_polls_before_entry=used,events=events,snapshots=snapshots,trace_metadata=metadata,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,events[-12:],flush=True)
