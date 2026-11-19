"""Focused contact, scripted voice and roar checks from existing nearby checkpoints."""
import json,csv,os,subprocess,struct
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard710-behavior';out.mkdir(exist_ok=True);cases={}
opening=json.loads((ROOT/'build/graveyard597-opening/report.json').read_text())['commands']['all']
late=json.loads((ROOT/'build/graveyard700-scripted-hyena/report.json').read_text())['commands']['md']
fresh=json.loads((ROOT/'build/graveyard685-skull/report.json').read_text())['commands']['md']
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,template,end,extra,load,pads in [
 ('bounds-snes',opening,13820,'gameplay.levels.elephant_graveyard.hyena_bounds = snes\n',None,None),
 ('bounds-md',opening,13820,'gameplay.levels.elephant_graveyard.hyena_bounds = md\n',None,None),
 ('scripted-voice',late,17530,'',ROOT/'build/graveyard709-scripted/observed.state',[0]*300),
 ('roar-snes',fresh,1680,'gameplay.simba.roar = snes\n',None,[0]*95+[0x80]*20+[0]*200),
 ('roar-md',fresh,1680,'gameplay.simba.roar = md\n',None,[0]*95+[0x80]*20+[0]*200)]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=template.copy();cmd[0]=str(ROOT/'build/graveyard708/player.exe')
 for flag,count in (('--save-at',3),('--wav',2),('--wav-seconds',2)):
  if flag in cmd:i=cmd.index(flag);del cmd[i:i+count]
 for flag,value in (('--frames',str(end)),('--hash-at',str(end)),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard707-helper/sprites.assets')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
 if load:cmd[cmd.index('--load')+1]=str(load)
 if pads is not None:
  (folder/'input.polled.tape').write_bytes(struct.pack('<'+'H'*len(pads),*pads));cmd[cmd.index('--input-polled')+1]=str(folder/'input.polled.tape')
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text()+'\ngameplay.levels.elephant_graveyard = snes\n' if name=='scripted-voice' else 'schema = 1\ngame = snes\ndisplay.viewport = md\naudio.music.elephant_graveyard = md\naudio.effects.world.hyena_hurt = md\naudio.effects.world.hyena_pant = md\naudio.effects.world.hyena_taunt = md\n'+extra)
 cmd+=['--wav',str(folder/'audio.wav'),'--wav-seconds','12']
 if name not in ('bounds-snes','bounds-md') or not (folder/'scene.json').exists():
  with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_HITBOX_TRACE=str(folder/'hitboxes.csv'),TLK_HYENA_VOICE_TRACE=str(folder/'voice.csv'),TLK_ROAR_TRACE=str(folder/'roar.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv'),TLK_GRAVEYARD_ACTOR_TRACE=str(folder/'actors.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
 def rows(n):return list(csv.DictReader((folder/n).open())) if (folder/n).exists() else []
 cases[name]=dict(command=cmd,hitboxes=rows('hitboxes.csv'),voices=rows('voice.csv'),roar=rows('roar.csv'),sounds=rows('commands.csv'),scene=json.loads((folder/'scene.json').read_text())['latched_gameplay'])
 print(name,'HP',cases[name]['scene']['health'],'hitboxes',len(cases[name]['hitboxes']),'voice',cases[name]['voices'],'roar',len(cases[name]['roar']),flush=True)
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),ROOT/'build/graveyard708/build-report.json',ROOT/'build/graveyard707-helper/build-report.json')}),indent=2)+'\n')
