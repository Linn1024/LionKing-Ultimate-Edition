"""Inspect real Windows socket/attack frames and qualify exact MD first-attack geometry."""
import json,os,subprocess,time,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from windows_json_pipe import JsonPipe
from windows_capture import capture_client
from verify_windows import USER32,window_for
from pride_sprite_catalog import md_frame,bitmap
reference=ROOT/'build/graveyard685-skull/report.json';r=bound(reference);assert r['result']=='PASS'
out=ROOT/'build/graveyard687-window';out.mkdir(exist_ok=True);cmd=r['commands']['md'].copy();cmd.remove('--no-pace')
for flag,value in (('--frames','1920'),('--hash-at','1920'),('--config',str(out/'host.ini')),('--resource-profile',str(out/'resources.ini')),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):cmd[cmd.index(flag)+1]=value
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');(out/'resources.ini').write_bytes((ROOT/'profiles/graveyard-md.ini').read_bytes())
trace=JsonPipe(out/'tree.jsonl.gz');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_SOFT_TREE_LOG']=trace.name;USER32.SetProcessDPIAware();captures={}
with (out/'run.log').open('wb') as log:
 proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  deadline=time.monotonic()+25
  while proc.poll() is None and time.monotonic()<deadline:
   row=trace.latest()
   if row and row['level']==2 and row['descriptor']==0xc003eb:
    for label,field in (('socket',1685),('convergence',1887)):
     if label not in captures and field<=row['field']<field+12:
      hwnd=window_for(proc.pid)
      if hwnd:capture_client(hwnd,out/(label+'-client.png'));captures[label]=row
   time.sleep(.005)
  proc.wait(timeout=10)
 finally:
  if proc.poll() is None:proc.terminate();proc.wait(timeout=5)
  trace.finish()
changes=r['md_changes'];right=next(x for x in changes if x['actor']=='b693' and x['action']=='c148b6');left=next(x for x in changes if x['actor']=='b813' and x['action']=='c148b6');rl=next(x for x in changes if x['actor']=='b693' and x['action']=='c14a97' and int(x['field'])>1800);ll=next(x for x in changes if x['actor']=='b813' and x['action']=='c14a97' and int(x['field'])>1800)
# Independently decode the original MD indexed pixels and compare installer payloads.
raw=(ROOT/'build/graveyard683-helper/sprites.assets').read_bytes();count=struct.unpack_from('<I',raw,20)[0];at=192+416+17792;records={}
for i in range(count):
 pose,a,b=struct.unpack_from('<III',raw,at);at+=12;records[pose]=raw[at:at+a];at+=a+b
m=(ROOT/'Lion King, The (World).md').read_bytes();ns=(0x1301,0x133c,0x1377,0x13b2,0x13ed,0x1428,0x1463,0x149a,0x14d1,0x1508,0x1557);ms=(0x8b226,0x8b28e,0x8b2f6,0x8b34e,0x8b3a6,0x8b3fe,0x8b446,0x8b48e,0x8b4e6,0x8b51e,0x8b586)
checks=dict(real_socket_client='socket' in captures,real_convergence_client='convergence' in captures,clean_exit=proc.returncode==0,right_jump_start_matches_md=int(right['x'])==1212,left_jump_start_matches_md=int(left['x'])==977,right_landing_matches_md=int(rl['x'])==1084,left_landing_matches_md=int(ll['x'])==1101,jump_separation_matches_md=int(left['field'])-int(right['field'])==3,all_11_socket_images_exact=all(records[p]==bitmap(m,md_frame(m,q),True,with_origin=True)[4] for p,q in zip(ns,ms)))
paths=[Path(__file__),reference,ROOT/'build/graveyard683-helper/build-report.json',ROOT/'build/graveyard684/build-report.json',ROOT/'build/graveyard657-md-skull/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,captures=captures,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
