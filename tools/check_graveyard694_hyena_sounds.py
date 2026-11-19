"""Audit the complete original regular-hyena sound inventory and current checkpoint playback."""
import csv,json,os,subprocess,re
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/graveyard694-hyena-sounds';out.mkdir(exist_ok=True)
opening=ROOT/'build/graveyard597-opening/report.json';a=bound(opening)
taunt=ROOT/'build/graveyard611-taunt/report.json';t=bound(taunt)
current=ROOT/'build/graveyard684/build-report.json';bound(current)
commands={};sounds={};entries={};stems={};actors={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for label,cmd in [('opening',a['commands']['all'].copy()),('taunt',t['command'].copy())]:
 folder=out/label;folder.mkdir(exist_ok=True);cmd[0]=str(ROOT/'dist/installed-preview684/LionKing.exe')
 if '--save-at' in cmd:
  i=cmd.index('--save-at');del cmd[i:i+3]
 for flag,value in (('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--sprite-assets',str(ROOT/'build/graveyard683-helper/sprites.assets')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json')),('--wav',str(folder/'audio.wav'))):cmd[cmd.index(flag)+1]=value
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n')
 # Keep the checkpoint's existing gameplay, so this checks the audio subsystem
 # without changing its route. Current MD turn/jump behavior was checked in685/692.
 (folder/'resources.ini').write_text('schema = 1\ngame = snes\ndisplay.viewport = md\naudio.music.elephant_graveyard = md\naudio.effects.simba.bounce = md\n'+''.join('audio.effects.world.hyena_'+name+' = md\n' for name in ('hurt','pant','taunt','jump')))
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_HYENA_VOICE_TRACE=str(folder/'voice.csv'),TLK_HYENA_TAUNT_TRACE=str(folder/'taunt.csv'),TLK_GRAVEYARD_ACTOR_TRACE=str(folder/'actors.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
 commands[label]=cmd;sounds[label]=list(csv.DictReader((folder/'commands.csv').open()));stems[label]=list(csv.DictReader((folder/'stems.csv').open()));actors[label]=list(csv.DictReader((folder/'actors.csv').open()));entries[label]={name:list(csv.DictReader((folder/(name+'.csv')).open())) if (folder/(name+'.csv')).exists() else [] for name in ('voice','taunt')}
 print(label,'cues',[(x['selector'],x['value']) for x in sounds[label]],flush=True)
checks=dict(current_installed_binary=digest(ROOT/'dist/installed-preview684/LionKing.exe')==json.loads(current.read_text())['binary_sha256'],reaction_pcm4=any(x['selector']=='19' and x['value']=='4' for x in sounds['opening']),pant_pcm7=any(x['selector']=='19' and x['value']=='7' for x in sounds['opening']),taunt_pcm3=any(x['selector']=='19' and x['value']=='3' for x in sounds['taunt']),stomp_contact_fm123=any(x['selector']=='2' and x['value']=='123' for x in sounds['opening']),reaction_once_per_entry=sum(x['selector']=='19' and x['value']=='4' for x in sounds['opening'])==sum(int(x['emitted']) for x in entries['opening']['voice']),taunt_once_per_entry=sum(x['selector']=='19' and x['value']=='3' for x in sounds['taunt'])==sum(int(x['emitted']) for x in entries['taunt']['taunt']),md_output_audible=all(any(int(x['md_peak'])>500 for x in rows) for rows in stems.values()),jump_independence_already_verified=bound(ROOT/'build/graveyard692-jump-voice/report.json')['result']=='PASS')
original=bound(ROOT/'build/graveyard591-cue-owners/report.json');inventory=[x for x in original['counts'] if x['descriptor']=='0x97964'];checks['original_regular_hyena_voice_inventory']={x['value'] for x in inventory if x['selector']==19}=={3,4,7}
paths=[Path(__file__),opening,taunt,current,ROOT/'build/graveyard591-cue-owners/report.json',ROOT/'build/graveyard692-jump-voice/report.json',ROOT/'engine/runner/tlk_hyena_audio.c',ROOT/'engine/runner/tlk_audio.c']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,original_regular_hyena_voice_inventory=inventory,entry_traces=entries,scope='Regular young-Simba hyenas in Graveyard: complete original PCM3/4/7 inventory, current installed checkpoint playback, once-per-entry triggers, MD output and stomp FM123. Physical leap is intentionally silent. Hurt/death actions19B904/19B9E0 have no separate sound call; shared FM165 defeat is19C554, outside the regular hyena chain. Other levels/adult enemies and universal action timing are not claimed.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,flush=True)
