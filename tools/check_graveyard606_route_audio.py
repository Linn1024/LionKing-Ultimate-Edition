"""One final combined Graveyard graphics/effects walkthrough, stopping at visible Stampede."""
import collections,csv,json,os,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/graveyard516-route/report.json';r=bound(reference);opening=ROOT/'build/graveyard597-opening/report.json';o=bound(opening);build=ROOT/'build/graveyard599/build-report.json';bound(build)
out=ROOT/'build/graveyard606-route-audio';out.mkdir(exist_ok=True);cmd=r['command'].copy();cmd[0]=str(build.parent/'player.exe');i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard529-helper/sprites.assets')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json')),('--wav',str(out/'audio.wav')),('--hash-at','13500,15500,18000')):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_text('opengl = 0\nscale = 3\n')
(out/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngraphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.hud = md\ngraphics.sprites.enemies.hyenas = md\ngraphics.sprites.enemies.vultures = md\ngraphics.sprites.bones.palette = md\naudio.music.elephant_graveyard = md\naudio.music.stampede = md\n'+''.join(x+' = md\n' for x in o['shared_leaves']+o['specific_leaves']))
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(TLK_SOFT_TREE_LOG=trace.name,TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv'));USER32.SetProcessDPIAware();hwnd=None;captures={};events=[];last=None;stampede=None;progress=0
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+180
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row:
                if row['field']//1000>progress:print('GRAVEYARD',row['field'],flush=True);progress=row['field']//1000
                key=tuple(row[k] for k in ('level','descriptor','health','lives'))
                if key!=last:events.append({k:row[k] for k in ('field','level','descriptor','health','lives')});last=key
                if not hwnd:hwnd=window_for(proc.pid)
                if hwnd and row['level']==2 and row['descriptor']==0xc003eb:
                    for name,field in (('vultures',15300),('pillar',16600),('final-fight',18000)):
                        if name not in captures and row['field']>=field:capture_client(hwnd,out/(name+'.png'));captures[name]={k:row[k] for k in ('field','level','descriptor','health')}
                if row['level']==3 and row['descriptor']==0xc0041d and row['health']>0:
                    if stampede is None:stampede=row['field']
                    if hwnd and row['field']>=stampede+120:capture_client(hwnd,out/'stampede.png');captures['stampede']={k:row[k] for k in ('field','level','descriptor','health')};USER32.PostMessageW(hwnd,0x10,0,0);break
            time.sleep(.01)
        proc.wait(timeout=10)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish()
counts=collections.Counter((x['selector'],x['value']) for x in csv.DictReader((out/'commands.csv').open()));expected=[('19','4'),('19','7'),('19','3'),('19','2'),('19','1'),('2','123'),('2','105'),('2','127'),('2','171'),('2','92'),('2','94'),('2','98'),('2','97'),('2','117'),('2','112'),('19','15')]
checks=dict(clean_exit=proc.returncode==0,profile_loaded='Saved resource profile loaded' in (out/'run.log').read_text(),all_exercised_effect_families=all(counts[k]>0 for k in expected),one_pillar_fall_and_impact=counts[('2','171')]==counts[('2','92')]==1,graveyard_track=counts[('1','83')]>0,reached_living_stampede='stampede' in captures and captures['stampede']['health']>0,actual_windows=len(captures)==4)
paths=[Path(__file__),reference,opening,build,ROOT/'build/graveyard604-pillar-qualified/report.json',ROOT/'build/graveyard603-lifecycle/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,events=events,captures=captures,sounds=[dict(selector=a[0],value=a[1],count=n) for a,n in counts.items()],trace_metadata=metadata,scope=__doc__,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,dict(counts),flush=True)
