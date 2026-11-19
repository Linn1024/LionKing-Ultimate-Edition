"""Fresh direct-selected Graveyard: native SPC song with independently selected MD effects."""
import collections,csv,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard505-entry/report.json';r=bound(reference);opening=ROOT/'build/graveyard597-opening/report.json';o=bound(opening);build=ROOT/'build/graveyard599/build-report.json';bound(build)
out=ROOT/'build/graveyard601-native-music';out.mkdir(exist_ok=True);profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'+''.join(x+' = md\n' for x in o['shared_leaves']+o['specific_leaves']))
(out/'host.ini').write_text('opengl = 0\nscale = 3\n');cmd=r['command'].copy();cmd[0]=str(build.parent/'player.exe')
for flag,value in (('--config',str(out/'host.ini')),('--resource-profile',str(profile)),('--sprite-assets',str(ROOT/'build/graveyard529-helper/sprites.assets')),('--dump-window',str(out/'entry.png')),('--dump-scene',str(out/'entry-scene.json'))):cmd[cmd.index(flag)+1]=value
cmd[-1]=str(out/'entry.state');env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'entry.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
play=cmd.copy();i=play.index('--save-at');del play[i:i+3];i=play.index('--practice-level');del play[i:i+2]
for flag,value in (('--frames','1830'),('--hash-at','1830'),('--dump-window',str(out/'window.png')),('--dump-scene',str(out/'scene.json'))):play[play.index(flag)+1]=value
play+=['--load',str(out/'entry.state'),'--input-polled',o['commands']['all'][o['commands']['all'].index('--input-polled')+1],'--wav',str(out/'audio.wav'),'--wav-seconds','6']
with (out/'run.log').open('wb') as log:subprocess.run(play,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(out/'commands.csv'),TLK_AUDIO_STEMS=str(out/'stems.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
counts=collections.Counter((x['selector'],x['value']) for x in csv.DictReader((out/'commands.csv').open()));stems=list(csv.DictReader((out/'stems.csv').open()));scene=json.loads((out/'scene.json').read_text())
checks=dict(fresh_native_song_entry=json.loads((out/'entry-scene.json').read_text())['level']==2,profile_loaded='Saved resource profile loaded' in (out/'run.log').read_text(),no_md_music=not any(k[0]=='1' and k[1]!='0' for k in counts),md_effects_emitted=bool(counts),both_sound_buses=any(int(x['native_peak'])>500 and int(x['md_peak'])>500 for x in stems),actual_playable_graveyard=scene['level']==2 and scene['latched_gameplay']['health']>0)
paths=[Path(__file__),reference,opening,build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=dict(seed=cmd,play=play),sounds=[dict(selector=a[0],value=a[1],count=n) for a,n in counts.items()],scope='Fresh native-music selection, not a stopped-SPC MD checkpoint; short normal controller excerpt tests audio mixing, not cross-route parity or full fresh-start completion.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'}),indent=2)+'\n');print(checks,dict(counts),flush=True)
