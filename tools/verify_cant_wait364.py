"""Check one moving fade save, pause ownership, and actual second-level window."""
import json,os,re,struct,subprocess,time
from pathlib import Path
from PIL import Image
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_process_read import PlayerRead
from verify_windows import USER32,window_for
from windows_capture import capture_client
reference=ROOT/'build/cant-wait363/report.json';ref=bound(reference);assert ref['result']=='PASS'
out=ROOT/'build/cant-wait364';out.mkdir(exist_ok=True);checks={};commands={}
base=ref['commands']['moving-new'].copy()
for flag,n in (('--practice-level',2),('--save-at',3)):
    i=base.index(flag);del base[i:i+n]
base+=['--load',str(reference.parent/'moving.state')]
clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
def command(label,field=2200):
    folder=out/label;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[cmd.index('--frames')+1]=str(field)
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):cmd[cmd.index(flag)+1]=str(folder/name)
    cmd[cmd.index('--hash-at')+1]=str(field);return folder,cmd
def run(label,cmd):
    commands[label]=cmd
    with (out/label/'run.log').open('wb') as log:return subprocess.run(cmd,cwd=ROOT,env=dict(clean,SDL_VIDEODRIVER='dummy'),stdout=log,stderr=subprocess.STDOUT,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW).returncode
folder,cmd=command('cold');rc=run('cold',cmd)
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda p:re.findall(pattern,p.read_text())
checks['moving_cold_guest']=rc==0 and rows(folder/'run.log')==[r for r in rows(reference.parent/'moving-new/run.log') if r[0]=='2200']
checks['moving_cold_picture']=digest(folder/'window.png')==digest(reference.parent/'moving-new/window.png')
folder,cmd=command('paused',1618);raw=bytearray((reference.parent/'move.tape').read_bytes());struct.pack_into('<H',raw,1611*2,0x1000);(out/'pause.tape').write_bytes(raw)
cmd[cmd.index('--input')+1]=str(out/'pause.tape');cmd+=['--save-at','1618',str(out/'paused.state')];rc1=run('paused',cmd)
folder,cmd=command('paused-later',1640);cmd[cmd.index('--load')+1]=str(out/'paused.state');cmd[cmd.index('--input')+1]=str(out/'pause.tape');cmd+=['--save-at','1640',str(out/'paused-later.state')];rc2=run('paused-later',cmd)
def view_state(path):
    data=path.read_bytes();at=data.find(b'TLKVIEW1');assert at>=0 and struct.unpack_from('<I',data,at+8)[0]==4
    return struct.unpack_from('<9I',data,at+80),data[at+116:at+316]
a,ca=view_state(out/'paused.state');b,cb=view_state(out/'paused-later.state')
checks['paused_palette_and_scroll_hold']=rc1==rc2==0 and a==b and ca==cb
folder,cmd=command('native-palette');profile=Path(cmd[cmd.index('--resource-profile')+1]);profile.write_text(profile.read_text()+'\ngraphics.scenery.palettes = snes\n');rc=run('native-palette',cmd)
checks['palette_independent']=rc==0 and digest(folder/'window.png')!=digest(out/'cold/window.png')
# A short real window starts from the current build's moving state.
folder,cmd=command('windows',2250)
for flag in ('--dump-window','--dump-scene','--wav'):
    i=cmd.index(flag);del cmd[i:i+2]
cmd.remove('--no-pace');USER32.SetProcessDPIAware();reader=None;before=after=None
with (folder/'run.log').open('wb') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        reader=PlayerRead(Path(cmd[0]),proc.pid);deadline=time.monotonic()+20
        while proc.poll() is None and time.monotonic()<deadline:
            before=reader.snapshot()
            if before['field']>=2180:
                hwnd=window_for(proc.pid)
                if hwnd:capture_client(hwnd,folder/'level.png');after=reader.snapshot();break
            time.sleep(.003)
        proc.wait(timeout=10)
    finally:
        if reader:reader.close()
        if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
checks['actual_second_level_window']=proc.returncode==0 and bool(after) and 2180<=before['field']<=after['field']<2250
paths=[Path(__file__),reference,ROOT/'build/cant-wait362/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,window_command=cmd,before=before,after=after,scope='One current moving color-transition save resumes exact guest/picture; paused state holds palette/scroll, palette choice independent, actual second-level Windows client. No older-save or unrelated suites.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n')
print(checks,flush=True)
