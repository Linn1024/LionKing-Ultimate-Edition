"""Focused Hakuna native control, independent death movement, roar and boss recovery."""
import json,os,subprocess,re,struct,csv
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna850-behavior';out.mkdir(exist_ok=True);cases={};checks={}
base=json.loads((ROOT/'build/hakuna830-hud/report.json').read_text())['cases']['native']['command']
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
def run(name,load,start,end,profile,pad=0,old=False,save=None):
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/('build/hakuna842/player.exe' if old else 'build/hakuna849/player.exe'))
 for flag,value in (('--load',ROOT/load),('--frames',end),('--hash-at',end),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+profile);(folder/'input.polled.tape').write_bytes(struct.pack('<H',pad)*4000);cmd+=['--input-polled',str(folder/'input.polled.tape')]
 if save:cmd+=['--save-at',str(save),str(folder/'current.state')]
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_ROAR_TRACE=str(folder/'roar.csv'),TLK_GORILLA_TIMING=str(folder/'gorilla.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
 scene=json.loads((folder/'scene.json').read_text());cases[name]=dict(command=cmd,window_sha256=digest(folder/'window.png'),guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),death=scene['graveyard_death'],gameplay=scene['latched_gameplay'],roar=list(csv.DictReader((folder/'roar.csv').open())) if (folder/'roar.csv').exists() else [],gorilla=list(csv.DictReader((folder/'gorilla.csv').open())) if (folder/'gorilla.csv').exists() else [],commands=list(csv.DictReader((folder/'commands.csv').open())));print(name,cases[name]['death'],'roar',len(cases[name]['roar']),'gorilla',cases[name]['gorilla'],flush=True)
 return cases[name]
fixture='build/hakuna844-deaths/5/before.native.state';motion='graphics.sprites.simba.cub.hakuna_death_motion = md\n'
run('old-native',fixture,36430,36580,'',old=True);run('native',fixture,36430,36580,'');run('motion',fixture,36430,36580,motion,save=36540)
run('restored','build/hakuna850-behavior/motion/current.state',36540,36580,motion)
run('retry','build/hakuna850-behavior/motion/current.state',36540,37030,motion)
boss='build/hakuna803-gorilla/encounter.native.state';run('boss-native',boss,35060,36450,'');run('boss-md',boss,35060,36450,'gameplay.levels.hakuna_matata.gorilla_recovery = md\n')
# SNES default layout: Y is the cub's roar. Start standing in the boss arena.
run('roar-native',boss,35060,35250,'',pad=0x4000);run('roar-md',boss,35060,35250,'gameplay.simba.roar = md\naudio.effects.simba.roar = md\n',pad=0x4000)
c=cases;checks=dict(native_preserved=c['old-native']['window_sha256']==c['native']['window_sha256'] and c['old-native']['guest']==c['native']['guest'],motion_visible=c['motion']['death']['selected']==1 and c['motion']['window_sha256']!=c['native']['window_sha256'],motion_guest_preserved=c['motion']['guest']==c['native']['guest'],current_save=c['motion']['window_sha256']==c['restored']['window_sha256'],retry_healthy=c['retry']['gameplay']['health']>0 and c['retry']['death']['selected']==0,gorilla_11=bool(c['boss-md']['gorilla']) and all(r['selected']=='11' for r in c['boss-md']['gorilla']),gorilla_native_untouched=not c['boss-native']['gorilla'],roar14=any(r['event']=='activation_delay' and r['value']=='14' for r in c['roar-md']['roar']),roar_voice=any(r['selector']=='19' and r['value']=='10' for r in c['roar-md']['commands']))
paths=[Path(__file__),ROOT/'build/hakuna849/build-report.json',ROOT/'build/hakuna847-tokens/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
