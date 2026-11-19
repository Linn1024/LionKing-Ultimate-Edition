"""Continue Return with MD contacts after an ordinary grounded-slash detour."""
import json,os,csv,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
from build_pride_compiled_hooks import digest
out=ROOT/'build/return915-adapted';out.mkdir(exist_ok=True);prior=json.loads((ROOT/'build/later914-combat/report.json').read_text());cmd=prior['cases']['slash']['command'].copy();i=cmd.index('--save-at');del cmd[i:i+3]
entry=prior['cases']['entry']['command'];used=int(re.search(r'tape_words_used=(\d+)',(ROOT/'build/later914-combat/entry/run.log').read_text())[1]);tape=Path(entry[entry.index('--input-polled')+1]).read_bytes();(out/'remaining.polled.tape').write_bytes(tape[used*2:])
for flag,value in (('--load',Path(prior['cases']['slash']['native_state'])),('--input-polled',out/'remaining.polled.tape'),('--frames',57500),('--hash-at',57500),('--resource-profile',ROOT/'profiles/return-md.ini'),('--config',out/'host.ini'),('--dump-window',out/'window.png'),('--dump-scene',out/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
cmd+=['--save-at','57500',str(out/'pride-rock.state')];(out/'host.ini').write_text('opengl = 0\nscale = 1\n');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_BG_TRACE=str(out/'scenes.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=70,creationflags=subprocess.CREATE_NO_WINDOW)
s=json.loads((out/'scene.json').read_text());levels=[]
for r in csv.DictReader((out/'scenes.csv').open()):
 level=int(r['level'])
 if not levels or levels[-1]['level']!=level:levels.append(dict(field=int(r['frame']),level=level))
used_tail=int(re.search(r'tape_words_used=(\d+)',(out/'run.log').read_text())[1]);(out/'after57500.polled.tape').write_bytes((out/'remaining.polled.tape').read_bytes()[used_tail*2:]);native_fixture(out/'pride-rock.state',out/'pride-rock.native.state',57500)
checks=dict(completed_return=s['level']==9,healthy=s['latched_gameplay']['health']>0,ordinary_combat_detour=prior['checks']['ordinary_inputs_only']);paths=[Path(__file__),ROOT/'build/later914-combat/report.json',ROOT/'build/later910/build-report.json',ROOT/'profiles/return-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'PARTIAL',checks=checks,scope='MD contacts, art/palette and voices. Ordinary grounded slashes replace the native recording first-fight assumption; no health, actor or collision cheats. Earlier approach/first fight is retained in914.',levels=levels,command=cmd,gameplay=s['latched_gameplay'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,levels,s['latched_gameplay'],flush=True)
