"""Bounded ordinary Graveyard health death/retry, with driver commands and real client captures."""
import csv,gzip,json,os,subprocess,sys,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
reference=ROOT/'build/graveyard629-controls/stomp2/report.json';r=bound(reference);build=ROOT/'build/graveyard635/build-report.json';bound(build)
name=sys.argv[1] if len(sys.argv)>1 else 'both';out=ROOT/'build/graveyard636-death'/name;out.mkdir(parents=True);cmd=r['command'].copy();cmd[0]=str(ROOT/('build/graveyard621/player.exe' if name=='old-native' else 'build/graveyard635/player.exe'))
profiles={'both':'audio.music.elephant_graveyard = md\n','level':'audio.music.elephant_graveyard.track = md\n','death':'audio.music.elephant_graveyard.death = md\n','native':'','old-native':''};profile='schema = 1\ngame = snes\n'+profiles[name]
for flag,value in (('--load',str(reference.parent/'entry.state')),('--input-polled',str(out/'idle.polled.tape')),('--frames','19800'),('--hash-at','18900,19200,19800'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json')),('--wav',str(out/'audio.wav')),('--wav-seconds','25')):cmd[cmd.index(flag)+1]=value
i=cmd.index('--save-at');del cmd[i:i+3]
(out/'idle.polled.tape').write_bytes(bytes(4000));(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_text(profile)
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(TLK_SOFT_TREE_LOG=trace.name,TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'),TLK_AUDIO_EVENTS=str(out/'events.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv'));captures={};USER32.SetProcessDPIAware()
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+45
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row:
                label='death' if row['health']==0 else 'retry' if 'death' in captures and row['lives']<8 else None
                if label and label not in captures:
                    hwnd=window_for(proc.pid)
                    if hwnd:capture_client(hwnd,out/(label+'.png'));captures[label]={k:row[k] for k in ('field','health','lives','level')}
            time.sleep(.006)
        proc.wait(timeout=10)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish()
rows=[json.loads(x) for x in gzip.open(out/'tree.jsonl.gz','rt')];events=[];last=None
for row in rows:
    key=tuple(row[k] for k in ('level','descriptor','health','lives'))
    if key!=last:events.append({k:row[k] for k in ('field','level','descriptor','health','lives')});last=key
commands=list(csv.DictReader((out/'commands.csv').open())) if (out/'commands.csv').exists() else [];music=[x for x in commands if x['selector']=='1'];paths=[Path(__file__),reference,build]
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',command=cmd,events=events,music=music,captures=captures,last={k:rows[-1][k] for k in ('field','level','health','lives')},source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(name,events,music,captures,flush=True)
