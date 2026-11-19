"""Final installed all-available-MD replay of the Genesis TAS gameplay inputs.

Only menu boot and console button names are translated. Original nonlag game
inputs keep their order; no branches, retries, guest edits or input searches.
"""
import csv,json,os,re,struct,subprocess,time,zipfile
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_capture import capture_client
from verify_windows import USER32,window_for
out=ROOT/'build/remaining1025-genesis-tas';out.mkdir(exist_ok=True);publication=ROOT/'build/remaining1020-publication/report.json';bound(publication)
movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2';ref=ROOT/'build/remaining1001-reference/frames.csv'
with zipfile.ZipFile(movie) as z:
 lines=[s for s in z.read('Input Log.txt').decode().splitlines() if s.startswith('|')];header=z.read('Header.txt').decode()
mapping=[0x800,0x400,0x200,0x100,0x80,0x4000,0x8000,0x1000,0x40,0,0,0]
pads=[]
for line in lines:
 fields=line.split('|');assert fields[1]=='..' and fields[3]=='.'*12
 assert fields[2][9:]=='.'*3,'Unmapped Y/Z/Mode buttons present'
 pads.append(sum(value for c,value in zip(fields[2],mapping) if c!='.'))
rows=list(csv.DictReader(ref.open()));events=[(int(r['field']),pads[int(r['field'])-1]) for r in rows if r['lag']=='0' and int(r['field'])<=len(pads)]
start=next(i for i,(f,p) in enumerate(events) if p&0x100);raw=(ROOT/'engine/tapes/allbugsF.read.tape').read_bytes();native=list(struct.unpack('<'+'H'*(len(raw)//2),raw));boot=(ROOT/'build/remaining1024-boot/prefix.polled.tape').read_bytes();prefix=list(struct.unpack('<'+'H'*(len(boot)//2),boot));converted=prefix+[p for f,p in events[start:]]
tape=out/'genesis-gameplay.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(converted),*converted));provenance=dict(author='ShgofcTAS',source='https://tasvideos.org/10612S',movie_fields=len(pads),snes_boot_polls=len(prefix),first_md_movement_field=events[start][0],mapped_md_polls=len(events)-start,translated_buttons='MD Up/Down/Left/Right/A/B/C/Start/X -> SNES Up/Down/Left/Right/A/Y/B/Start/X; Y/Z/Mode unused',gameplay_inputs_changed=False,guest_edits=False)
(out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
cmd=[os.environ['COMSPEC'],'/d','/c',str(ROOT/'Play Available MD.cmd'),'-Frames','65000','-InputTape',str(tape),'-NoPace','-NoAudio','-WindowCapture',str(out/'window.png'),'-SceneCapture',str(out/'scene.json')]
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_BG_TRACE']=str(out/'scenes.csv');USER32.SetProcessDPIAware();captured=False;boot_observed=None;ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
with (out/'launcher.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  deadline=time.monotonic()+720;last_notice=0
  while proc.poll() is None and time.monotonic()<deadline:
   path=out/'scenes.csv';field=0
   if path.exists():
    with path.open('rb') as f:
     f.seek(max(0,path.stat().st_size-4096));tail=f.read().splitlines()
    for line in reversed(tail[:-1]):
     try:field=int(line.split(b',')[0]);break
     except ValueError:continue
   if field>=2500 and not captured:
    query="Get-CimInstance Win32_Process -Filter \"Name='LionKing.exe'\" | Where-Object { $_.CommandLine -like '*settings\\available-md*' } | Select-Object -ExpandProperty ProcessId"
    pids=subprocess.check_output([ps,'-NoProfile','-Command',query],creationflags=subprocess.CREATE_NO_WINDOW,text=True)
    for pid in pids.split():
     hwnd=window_for(int(pid))
     if hwnd:
      capture_client(hwnd,out/'actual.png');captured=True
      from read_windows_guest import guest_words
      boot_observed=guest_words(ROOT/'dist/installed-preview1014/LionKing.exe','available-md',dict(difficulty=0x1ff92,level=0x1ff9e,lives=0x1ffaa,health=0x2004,age=0x2000))
      assert boot_observed['difficulty']==0,('INVALID BOOT',boot_observed)
      break
   if field-last_notice>=10000:print('installed TAS field',field,flush=True);last_notice=field
   time.sleep(.2)
  proc.wait(timeout=5)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
runlog=ROOT/'settings/available-md/last-launch.log';text=runlog.read_text();(out/'player.log').write_text(text);scene=json.loads((out/'scene.json').read_text());transitions=[]
for r in csv.DictReader((out/'scenes.csv').open()):
 n=int(r['level'])
 if not transitions or transitions[-1]['level']!=n:transitions.append(dict(field=int(r['frame']),level=n))
used=re.search(r'tape_words_used=(\d+)/(\d+)',text);profile=ROOT/'settings/available-md/resources.ini';checks=dict(confirmed_easy_boot=bool(boot_observed and boot_observed['difficulty']==0),clean_exit=proc.returncode==0,profile_loaded='Saved resource profile loaded' in text,exact_available_md_profile=digest(profile)==digest(ROOT/'profiles/available-md.ini'),all_recorded_inputs_consumed=bool(used and int(used[1])==int(used[2])==len(converted)),all_main_levels=set(range(10))<=set(r['level'] for r in transitions),victory_or_credits=scene['latched_gameplay']['descriptor'] in (0x7a9,0x83f),actual_window_captured=captured)
paths=[Path(__file__),publication,ROOT/'build/remaining1024-boot/report.json',ROOT/'tools/read_windows_guest.py',movie,ref,tape,profile,ROOT/'profiles/available-md.ini',ROOT/'Play Available MD.cmd',ROOT/'dist/installed-preview1014/LionKing.exe']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,provenance=provenance,boot_observed=boot_observed,transitions=transitions,final_gameplay=scene['latched_gameplay'],tape_words_used=int(used[1]) if used else None,tape_words_total=len(converted),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('FINAL GENESIS TAS',checks,transitions,scene['latched_gameplay'],flush=True)
