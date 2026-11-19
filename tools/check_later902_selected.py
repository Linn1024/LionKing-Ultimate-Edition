"""Complete7/8 with the final selected resources and retain the exact Pride Rock input boundary."""
import json,os,csv,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/later902-selected';out.mkdir(exist_ok=True);cmd=json.loads((ROOT/'build/later872-route/report.json').read_text())['command'].copy();cmd[0]=str(ROOT/'build/later901/player.exe');i=cmd.index('--save-at');del cmd[i:i+3]
for flag,value in (('--frames',57000),('--hash-at',57000),('--sprite-assets',ROOT/'build/later882-helper/sprites.assets'),('--config',out/'host.ini'),('--resource-profile',ROOT/'profiles/be-prepared-md.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at','57000',str(out/'pride-rock.state')];(out/'host.ini').write_text('opengl = 0\nscale = 1\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_BG_TRACE=str(out/'scenes.csv'),TLK_MD_SOUND_COMMANDS=str(out/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=140,creationflags=subprocess.CREATE_NO_WINDOW)
used=int(re.search(r'tape_words_used=(\d+)',(out/'run.log').read_text())[1]);data=Path(cmd[cmd.index('--input-polled')+1]).read_bytes();(out/'after57000.polled.tape').write_bytes(data[used*2:]);native_fixture(out/'pride-rock.state',out/'pride-rock.native.state',57000);s=json.loads((out/'scene.json').read_text());levels=[]
for r in csv.DictReader((out/'scenes.csv').open()):
 level=int(r['level'])
 if not levels or levels[-1]['level']!=level:levels.append(dict(field=int(r['frame']),level=level))
checks=dict(completed_be_prepared=any(r['level']==8 for r in levels),completed_return=s['level']==9,healthy=s['latched_gameplay']['health']>0,exact_next_input=0<used<len(data)//2);paths=[Path(__file__),ROOT/'build/later901/build-report.json',ROOT/'profiles/be-prepared-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'PARTIAL',checks=checks,scope='Final selected7/8 resource walkthrough into Pride Rock. Other native AI/timing and unsupported scene9 resources retained; this does not establish the final ending.',levels=levels,command=cmd,used_polls=used,gameplay=s['latched_gameplay'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,levels,s['latched_gameplay'],flush=True)
