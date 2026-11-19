"""Check independent SNES jump voice remains audible with MD skull gameplay/music."""
import json,csv,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard685-skull/report.json';r=bound(reference);out=ROOT/'build/graveyard692-jump-voice';out.mkdir(exist_ok=True);commands={};traces={};stems={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for choice in ('md','snes'):
 folder=out/choice;folder.mkdir(exist_ok=True);cmd=r['commands']['md'].copy();cmd[0]=str(ROOT/'dist/installed-preview684/LionKing.exe')
 for flag,value in (('--frames','1910'),('--hash-at','1910'),('--config',str(folder/'host.ini')),('--resource-profile',str(folder/'resources.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
 (folder/'host.ini').write_text('opengl = 0\nscale = 3\n');(folder/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text()+'\naudio.effects.world.hyena_jump = '+choice+'\n')
 cmd+=['--wav',str(folder/'audio.wav'),'--wav-seconds','8']
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_GRAVEYARD_ACTOR_TRACE=str(folder/'actors.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=25,creationflags=subprocess.CREATE_NO_WINDOW)
 commands[choice]=cmd;traces[choice]=(folder/'actors.csv').read_bytes();stems[choice]=list(csv.DictReader((folder/'stems.csv').open()));print(choice,'done',flush=True)
peaks={c:max(int(x['native_peak']) for x in rows if 1852<=int(x['frame'])<=1870) for c,rows in stems.items()}
checks=dict(gameplay_choices_independent=traces['md']==traces['snes'],md_leap_voice_silent=peaks['md']==0,snes_leap_voice_audible=peaks['snes']>500)
paths=[Path(__file__),reference,ROOT/'build/graveyard691-original-jump-voice/report.json',ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/runner/tlk_resources.c']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,jump_window_native_peaks=peaks,commands=commands,scope='Original MD inward leaps are silent. Existing independent Hyena jump SNES choice restores the native voice with MD gameplay/music. No game code, assets or user settings changed.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,peaks,flush=True)
