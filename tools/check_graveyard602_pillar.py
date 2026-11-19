"""Isolate the long selected pillar effect from its checkpoint with bounded live progress/capture."""
import collections,csv,json,os,subprocess,time,gzip
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/graveyard597-opening/report.json';r=bound(reference);fixture=ROOT/'build/graveyard592-native-owners/report.json';bound(fixture);build=ROOT/'build/graveyard599/build-report.json';bound(build)
out=ROOT/'build/graveyard602-pillar';out.mkdir(exist_ok=True);cmd=r['commands']['native'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,value in (('--frames','17000'),('--hash-at','16450,17000'),('--load',str(fixture.parent/'15280/entry.state')),('--input-polled',str(fixture.parent/'15280/remaining.polled.tape')),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json')),('--wav',str(out/'audio.wav')),('--wav-seconds','1')):cmd[cmd.index(flag)+1]=value
cmd+=['--save-at','16450',str(out/'pending.state')]
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_text('schema = 1\ngame = snes\naudio.effects.world.graveyard.pillar = md\n')
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(TLK_SOFT_TREE_LOG=trace.name,TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv'));USER32.SetProcessDPIAware();hwnd=None;captured=False;last=0
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+90
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row:
                if row['field']//250>last:print('PILLAR',row['field'],flush=True);last=row['field']//250
                if not captured and row['field']>=16700:
                    hwnd=window_for(proc.pid)
                    if hwnd:capture_client(hwnd,out/'fall.png');captured=True
            time.sleep(.01)
        proc.wait(timeout=5)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish()
counts=collections.Counter((x['selector'],x['value']) for x in csv.DictReader((out/'commands.csv').open()));stems=list(csv.DictReader((out/'stems.csv').open()));rows=[json.loads(x) for x in gzip.open(out/'tree.jsonl.gz','rt')];saved=next(x for x in rows if x['field']==16450);tape=Path(cmd[cmd.index('--input-polled')+1]);(out/'pending.polled.tape').write_bytes(tape.read_bytes()[saved['poll_index']*2:])
checks=dict(exit=proc.returncode==0,fall_and_impact=counts=={('2','171'):1,('2','92'):1},long_pillar_bus=any(int(x['frame'])>16800 and int(x['md_peak'])>100 for x in stems),actual_window=captured,actual_graveyard=rows[-1]['level']==2)
paths=[Path(__file__),reference,fixture,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,counts=[dict(selector=a[0],value=a[1],count=n) for a,n in counts.items()],trace_metadata=metadata,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,dict(counts),flush=True)
