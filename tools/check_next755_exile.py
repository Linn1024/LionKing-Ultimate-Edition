"""Focused new rock-sound source and final Exile progression from the current save."""
import json,gzip,os,subprocess,csv
from audit_scenes import ROOT
from next_level_checkpoint import native_fixture
out=ROOT/'build/next755-exile';out.mkdir(exist_ok=True);reference=json.loads((ROOT/'build/next752-route/report.json').read_text());base=reference['command'];used=reference['captures']['exile']['poll_index'];assert used==4759
tape=out/'after24500.polled.tape';tape.write_bytes((ROOT/'build/next752-route/continuation.polled.tape').read_bytes()[used*2:])
state=native_fixture(ROOT/'build/next752-route/exile.state',out/'entry.native.state')
cases={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for source,end in (('snes',24700),('md',27000)):
 folder=out/source;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/'build/next754/player.exe')
 i=cmd.index('--save-at');del cmd[i:i+3]
 for flag,value in (('--load',str(state)),('--input-polled',str(tape)),('--frames',str(end)),('--hash-at',str(end)),('--resource-profile',str(folder/'resources.ini')),('--config',str(folder/'host.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
 (folder/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text()+'\naudio.effects.world.simbas_exile.rocks = '+source+'\n');(folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60,creationflags=subprocess.CREATE_NO_WINDOW)
 commands=list(csv.DictReader((folder/'commands.csv').open()));scene=json.loads((folder/'scene.json').read_text());cases[source]=dict(command=cmd,rock_commands=sum(r['selector']=='2' and r['value']=='165' for r in commands),level=scene['level'],gameplay=scene['latched_gameplay']);print(source,cases[source]['rock_commands'],scene['level'],scene['latched_gameplay'],flush=True)
checks=dict(md_rock_sound=cases['md']['rock_commands']>0,snes_rock_choice_independent=cases['snes']['rock_commands']==0,exile_completed_alive=cases['md']['level']==5 and cases['md']['gameplay']['health']>0)
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases),indent=2)+'\n');print(checks)
