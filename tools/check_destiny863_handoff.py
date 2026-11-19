"""Verify final installed Destiny resource stack and author the next input boundary once."""
import json,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/destiny863-handoff';out.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/hakuna816-actors/report.json').read_text())['cases']['6-both']['command'].copy();cmd[0]=str(ROOT/'dist/installed-preview849/LionKing.exe');m=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'))
for flag,value in (('--frames',44500),('--hash-at',44500),('--config',out/'host.ini'),('--resource-profile',ROOT/'profiles/destiny-md.ini'),('--asset-cache',ROOT/'game-data'/m['scene_cache']['file']),('--sprite-assets',ROOT/'game-data'/m['sprite_assets']['file']),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at','44500',str(out/'current.state')];(out/'host.ini').write_text('opengl = 0\nscale = 1\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=70,creationflags=subprocess.CREATE_NO_WINDOW)
used=int(re.search(r'tape_words_used=(\d+)',(out/'run.log').read_text())[1]);tape=Path(cmd[cmd.index('--input-polled')+1]).read_bytes();(out/'after44500.polled.tape').write_bytes(tape[used*2:]);native_fixture(out/'current.state',out/'be-prepared.native.state',44500)
s=json.loads((out/'scene.json').read_text());checks=dict(healthy_be_prepared=s['level']==7 and s['stage_detected'] and s['latched_gameplay']['health']>0,remaining_input_boundary=0<used<len(tape)//2,current_native_checkpoint=(out/'be-prepared.native.state').exists())
paths=[Path(__file__),ROOT/'build/hakuna860-publication/report.json',ROOT/'profiles/destiny-md.ini',ROOT/'game-data/install.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,command=cmd,consumed_polls=used,gameplay=s['latched_gameplay'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,s['latched_gameplay'],flush=True)
