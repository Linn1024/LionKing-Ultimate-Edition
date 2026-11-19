"""Visible Mixed Graphics regression at a reproduced narrow-HUD frame."""
import csv,json,os,re,subprocess,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
build=ROOT/'build/hyena-hud356/build-report.json';bound(build)
oldproof=ROOT/'build/hyena-hud354/report.json';old=bound(oldproof)
proof=ROOT/'build/hyena-hud357/report.json';new=bound(proof)
out=ROOT/'build/hyena-hud358';out.mkdir(exist_ok=True);commands={}
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
def run(version):
    folder=out/version;folder.mkdir(exist_ok=True);cmd=new['command'].copy()
    cmd[0]=str(ROOT/('build/level-caption349/player.exe' if version=='old' else 'build/hyena-hud356/player.exe'))
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(folder/name)
    cmd[cmd.index('--frames')+1]='3852';cmd[cmd.index('--hash-at')+1]='3852';commands[version]=cmd
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=dict(clean,SDL_VIDEODRIVER='dummy'),stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    return version,rc
with ThreadPoolExecutor(max_workers=2) as pool:exits=dict(pool.map(run,('old','new')))
rows=lambda path:list(csv.DictReader(path.open()))
a=rows(oldproof.parent/'layout.csv');b=rows(proof.parent/'layout.csv')
missing=[int(r['field']) for r in a if r['pieces']=='0'];checks=dict(reproduced_six_old_failures=len(missing)==6,new_all_852_fields_have_meters=len(b)==852 and all(int(r['roar'])>0 and int(r['health'])>0 for r in b),fixed_all_old_missing_fields=all(any(int(r['field'])==n and int(r['pieces'])>0 for r in b) for n in missing),snapshot_exits=all(v==0 for v in exits.values()))
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda path:re.findall(pattern,path.read_text())
checks['trace_guest_unchanged']=hashes(oldproof.parent/'run.log')==hashes(proof.parent/'run.log')
checks['snapshot_guest_unchanged']=bool(hashes(out/'new/run.log')) and hashes(out/'new/run.log')==hashes(out/'old/run.log')
checks['snapshot_presentation_fixed']=digest(out/'new/window.png')!=digest(out/'old/window.png')
folder=out/'windows';folder.mkdir(exist_ok=True);cmd=commands['new'].copy()
for flag in ('--dump-window','--dump-scene'):
    i=cmd.index(flag);del cmd[i:i+2]
cmd[cmd.index('--frames')+1]='4020';USER32.SetProcessDPIAware();reader=None;before=after=None
with (folder/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(Path(cmd[0]),proc.pid);deadline=time.monotonic()+60
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=3850:
                hwnd=window_for(proc.pid)
                if hwnd:capture_client(hwnd,folder/'fight.png');after=reader.snapshot();break
            time.sleep(.002)
        proc.wait(timeout=20)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
checks['actual_windows_fight']=proc.returncode==0 and bool(after) and 3850<=before['field']<=after['field']<4020
paths=[Path(__file__),build,oldproof,proof]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,missing_old_fields=missing,commands=commands,window_command=cmd,before=before,after=after,scope='Focused reported Mixed Graphics hyena flicker. Exact OAM reuploads retain object metadata, all six reproduced frames fixed; native guest unchanged. Before/after rendered frame and real Windows fight view; no unrelated suites.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
