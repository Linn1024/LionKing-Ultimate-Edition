"""Traverse Hakuna with adapted backgrounds, keeping useful nearby saves."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/hakuna790-route';out.mkdir(exist_ok=True);bound(ROOT/'build/hakuna786/build-report.json');cases=[]
base=json.loads((ROOT/'build/hakuna781-native/report.json').read_text())['command'];env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
state=ROOT/'build/hakuna781-native/entry.native.state';tape=(ROOT/'build/hakuna781-native/after27000.polled.tape').read_bytes();start=27000
for end in (31000,34500,37000):
 folder=out/str(end);folder.mkdir(exist_ok=True);(folder/'input.polled.tape').write_bytes(tape);(folder/'host.ini').write_text('opengl = 0\nscale = 1\n');cmd=base.copy();cmd[0]=str(ROOT/'build/hakuna786/player.exe')
 while '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
 for flag,value in (('--load',state),('--input-polled',folder/'input.polled.tape'),('--config',folder/'host.ini'),('--resource-profile',ROOT/'build/hakuna789-player/5-md/resources.ini'),('--asset-cache',ROOT/'build/hakuna787-helper/scenes.cache'),('--frames',end),('--hash-at',end),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 state=folder/'current.state';cmd+=['--save-at',str(end),str(state)]
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=50,creationflags=subprocess.CREATE_NO_WINDOW)
 text=(folder/'run.log').read_text();used=int(re.search(r'tape_words_used=(\d+)',text)[1]);tape=tape[used*2:];s=json.loads((folder/'scene.json').read_text());cases.append(dict(start=start,end=end,level=s['level'],gameplay=s['latched_gameplay'],waterfall=s['hakuna_waterfall'],used_polls=used,command=cmd));start=end
 print(end,s['level'],s['latched_gameplay'],s['hakuna_waterfall'],flush=True)
(out/'after37000.polled.tape').write_bytes(tape)
checks=dict(healthy_vertical_section=cases[0]['level']==5 and cases[0]['gameplay']['health']>0,healthy_gorilla_section=cases[1]['level']==5 and cases[1]['gameplay']['health']>0,reached_healthy_adult_destiny=cases[-1]['level']==6 and cases[-1]['gameplay']['age']==65535 and cases[-1]['gameplay']['health']>0)
paths=[Path(__file__),ROOT/'build/hakuna786/build-report.json',ROOT/'build/hakuna787-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
