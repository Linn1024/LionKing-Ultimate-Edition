"""Direct level2 route with implemented graphics and MD music; bounded live captures."""
import csv,json,os,struct,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/cant-wait462-rhino/report.json';r=bound(reference)
build=ROOT/'build/cant-wait482/build-report.json';bound(build)
out=ROOT/'build/cant-wait484-route';out.mkdir(exist_ok=True)
rows=[line.split() for line in (ROOT/'build/cant-wait-native/aot/route.ram').read_text().splitlines()]
entry=next(i for i,x in enumerate(rows) if int(x[6],16)==1 and int(x[4],16)==66 and 380<=int(x[5],16)<=400 and int(x[3],16)>0)
used=sum(x[1]=='0' for x in rows[:entry]);assert used==4235
source=ROOT/'engine/tapes/allbugsF.read.tape';tape=out/'level2.polled.tape';tape.write_bytes(source.read_bytes()[used*2:])
cmd=r['commands']['native'].copy();cmd[0]=str(build.parent/'player.exe');i=cmd.index('--input');del cmd[i:i+2]
cmd+=['--input-polled',str(tape),'--wav',str(out/'audio.wav'),'--wav-seconds','1']
cmd[cmd.index('--frames')+1]='11000';cmd[cmd.index('--hash-at')+1]='1800,4000,7000,10000'
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(out/name)
(out/'host.ini').write_text('opengl = 0\nscale = 3\n')
(out/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.sprites.animals = md\ngraphics.hud = md\naudio.music.cant_wait_to_be_king = md\naudio.music.elephant_graveyard = md\n')
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(TLK_SOFT_TREE_LOG=trace.name,TLK_MD_SOUND_COMMANDS=str(out/'music.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv'))
USER32.SetProcessDPIAware();hwnd=None;events=[];last=None;snapshots={};next_entry=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+110
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row:
                key=tuple(row[k] for k in ('level','descriptor','health','lives'))
                if key!=last:events.append({k:row[k] for k in ('field','level','descriptor','health','lives','poll_index','macro_index','macro_length')});last=key
                if not hwnd:hwnd=window_for(proc.pid)
                if hwnd and row['level']==1 and row['descriptor']==0xc003b9 and row['health']>0:
                    for name,field in (('first-puzzle',2200),('ride',4300),('later-puzzle',6500)):
                        if name not in snapshots and row['field']>=field:
                            capture_client(hwnd,out/(name+'.png'));snapshots[name]=row
                if row['level']==2 and row['descriptor']==0xc003eb and row['health']>0:
                    if next_entry is None:next_entry=row['field']
                    if hwnd and row['field']>=next_entry+180:
                        capture_client(hwnd,out/'graveyard.png');snapshots['graveyard']=row;USER32.PostMessageW(hwnd,0x10,0,0);break
            time.sleep(.008)
        proc.wait(timeout=15)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish()
music=list(csv.DictReader((out/'music.csv').open()));stems=list(csv.DictReader((out/'stems.csv').open()))
checks=dict(exit=proc.returncode==0,direct_level_select=True,second_level_entered=any(e['level']==1 and e['descriptor']==0xc003b9 for e in events),reached_graveyard='graveyard' in snapshots,md_theme_command=any(c['selector']=='1' and c['value']=='2' for c in music),md_audio_rendered=any(int(v['md_peak'])>500 for v in stems),actual_windows=len(snapshots)>=3)
paths=[Path(__file__),reference,build,source,ROOT/'build/cant-wait-native/aot/route.ram']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'ROUTE_INCOMPLETE',checks=checks,command=cmd,original_entry_field=entry+1,original_polls_before_entry=used,events=events,snapshots=snapshots,trace_metadata=metadata,scope='One direct-selected second-level controller route with current implemented graphics and MD level music; bounded actual Windows images and one-second WAV plus complete stem/command diagnostics. No level1 replay, guest edits or universal timing equality claim.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,events[-12:],flush=True)
