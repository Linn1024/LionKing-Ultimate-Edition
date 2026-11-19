"""One combined second-level walkthrough, native music plus MD effects, reusable ride checkpoint."""
import collections,csv,gzip,json,os,re,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/cant-wait485-route/report.json';r=bound(reference)
build=ROOT/'build/cant-wait565/build-report.json';bound(build)
out=ROOT/'build/cant-wait567-route-audio';out.mkdir(exist_ok=True)
profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.sprites.animals = md\ngraphics.hud = md\naudio.effects = md\n')
host=out/'host.ini';host.write_text('opengl = 0\nscale = 3\n')
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
def adjust(cmd):
    cmd=cmd.copy();cmd[0]=str(build.parent/'player.exe')
    for flag,value in (('--config',str(host)),('--resource-profile',str(profile)),('--sprite-assets',str(ROOT/'build/graveyard529-helper/sprites.assets')),('--wav-seconds','4')):cmd[cmd.index(flag)+1]=value
    return cmd
seed=adjust(r['seed_command']);state=out/'entry.state';seed[-1]=str(state)
for flag,name in (('--dump-window','entry.png'),('--dump-scene','entry-scene.json'),('--wav','entry.wav')):seed[seed.index(flag)+1]=str(out/name)
with (out/'entry.log').open('wb') as log:subprocess.run(seed,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
cmd=adjust(r['command']);cmd[cmd.index('--load')+1]=str(state)
cmd[cmd.index('--hash-at')+1]='2130,4300,7000,10000,11000'
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(out/name)
cmd+=['--save-at','3700',str(out/'ride.state')]
trace=JsonPipe(out/'tree.jsonl.gz');runenv=dict(env,TLK_SOFT_TREE_LOG=trace.name,TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv'))
USER32.SetProcessDPIAware();captures={};hwnd=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=runenv,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+100
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row:
                if not hwnd:hwnd=window_for(proc.pid)
                if hwnd:
                    for name,field in (('ride',4300),('late-monkeys',7000)):
                        if name not in captures and row['field']>=field:capture_client(hwnd,out/(name+'.png'));captures[name]={k:row[k] for k in ('field','level','descriptor','health')}
            time.sleep(.01)
        proc.wait(timeout=10)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        traceinfo=trace.finish()
rows=[json.loads(x) for x in gzip.open(out/'tree.jsonl.gz','rt')]
saved=next(x for x in rows if x['field']==3700);tape=Path(cmd[cmd.index('--input-polled')+1]);(out/'ride.polled.tape').write_bytes(tape.read_bytes()[saved['poll_index']*2:])
counts=collections.Counter((x['selector'],x['value']) for x in csv.DictReader((out/'commands.csv').open()))
stems=list(csv.DictReader((out/'stems.csv').open()));scene=json.loads((out/'scene.json').read_text())
expected=[('2','106'),('2','119'),('19','8'),('19','10'),('2','94'),('2','169'),('19','5'),('2','101'),('19','15'),('2','112')]
checks=dict(exit=proc.returncode==0,native_music_no_md_track=not any(k[0]=='1' and k[1]!='0' for k in counts),all_cue_families=all(counts[k]>0 for k in expected),native_and_md_sound=any(int(x['native_peak'])>500 and int(x['md_peak'])>500 for x in stems),reached_graveyard=any(x['level']==2 and x['descriptor']==0xc003eb and x['health']>0 for x in rows),actual_windows=len(captures)==2)
paths=[Path(__file__),reference,build,ROOT/'build/cant-wait566-animation-cues/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=dict(seed=seed,route=cmd),counts=[dict(selector=k[0],value=k[1],count=v) for k,v in counts.items()],captures=captures,trace_metadata=traceinfo,ride_input_words=saved['poll_index'],final_gameplay=scene['latched_gameplay'],scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,dict(counts),flush=True)
