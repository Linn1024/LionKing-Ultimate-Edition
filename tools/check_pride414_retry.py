"""One ordinary nonfinal-death continuation with the full Available MD preset."""
import json,os,struct,subprocess,time
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/pride411-save/report.json';r=bound(reference);assert r['result']=='PASS'
out=ROOT/'build/pride414-retry';out.mkdir(exist_ok=True);cmd=r['commands']['resume'].copy()
original=Path(cmd[cmd.index('--input-polled')+1]).read_bytes();branch=out/'ordinary.polled.tape'
branch.write_bytes(original[:32*2]+bytes(5000*2));cmd[cmd.index('--input-polled')+1]=str(branch)
cmd[cmd.index('--frames')+1]='7400';cmd[cmd.index('--hash-at')+1]='6000,7400'
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(out/name)
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name
USER32.SetProcessDPIAware();death=revived=after=None;hwnd=None;events=[];previous=None
with (out/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        deadline=time.monotonic()+90
        while proc.poll() is None and time.monotonic()<deadline:
            row=trace.latest()
            if row:
                key=tuple(row[name] for name in ('level','descriptor','health','lives'))
                if key!=previous:events.append({name:row[name] for name in ('field','level','descriptor','health','lives')});previous=key
                pride=row['level']==0 and row['descriptor'] in (0xc00387,0xc0080d)
                if not death and pride and not row['health']:death=row
                if death and not revived and pride and row['health']>0 and row['lives']<8:revived=row
                if revived and pride and row['health']>0 and row['lives']==7 and row['field']>=revived['field']+120:
                    hwnd=window_for(proc.pid)
                    if hwnd:
                        capture_client(hwnd,out/'revived.png');after=trace.latest();USER32.PostMessageW(hwnd,0x10,0,0);break
            time.sleep(.008)
        proc.wait(timeout=15)
    finally:
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
        metadata=trace.finish()
scene=json.loads((out/'scene.json').read_text());game=scene['latched_gameplay']
checks=dict(exit=proc.returncode==0,ordinary_health_death_observed=bool(death),nonfinal_revival_observed=bool(revived),one_spare_life_consumed=bool(revived) and revived['lives']==7,actual_resumed_world=bool(after) and after['level']==0 and after['descriptor'] in (0xc00387,0xc0080d) and after['health']>0 and game['health']>0)
paths=[Path(__file__),reference]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE_ROUTE',checks=checks,command=cmd,events=events,death=death,revived=revived,after=after,trace_metadata=metadata,scope='One current published all-available-MD checkpoint,32 ordinary recorded polls into the fight then neutral controls. Observe natural health death and nonfinal retry with stock7, actual Windows world. No guest edits, old-save or timing/source/mode matrix; no original timing equivalence inferred.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,events[-12:],flush=True)
