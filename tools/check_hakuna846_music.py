"""Focused native death/retry, independent music sources and overlap checks for5/6."""
import csv,json,os,subprocess,re
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna846-music';out.mkdir(exist_ok=True);cases={};checks={}
base=json.loads((ROOT/'build/hakuna830-hud/report.json').read_text())['cases']['native']['command']
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for level,start,fixture,source,track in [(5,36430,'build/hakuna844-deaths/5/before.native.state','hakuna_matata',40),(6,38641,'build/hakuna845-adult/before.native.state','simbas_destiny',281)]:
 for name,extra,old in [('old-native','',True),('native','',False),('md',f'audio.music.{source} = md\n',False),('native-death',f'audio.music.{source} = md\naudio.music.{source}.death = snes\n',False)]:
  label=f'{level}-{name}';folder=out/label;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/('build/hakuna829/player.exe' if old else 'build/hakuna842/player.exe'));end=start+(200 if name in ('native','old-native') else 600)
  for flag,value in (('--load',ROOT/fixture),('--frames',end),('--hash-at',end),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
  (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+extra);cmd+=['--input-polled',str(folder/'neutral.polled.tape'),'--wav',str(folder/'audio.wav'),'--wav-seconds','20'];(folder/'neutral.polled.tape').write_bytes(bytes(3000))
  with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
  cmds=list(csv.DictReader((folder/'commands.csv').open()));stems=list(csv.DictReader((folder/'stems.csv').open()));hold=[r for r in stems if start+120<=int(r['frame'])<=start+200];scene=json.loads((folder/'scene.json').read_text());cases[label]=dict(command=cmd,music=[int(r['value']) for r in cmds if r['selector']=='1'],guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),window_sha256=digest(folder/'window.png'),audio_sha256=digest(folder/'audio.wav'),hold_native_peak=max((int(r['native_peak']) for r in hold),default=0),hold_md_peak=max((int(r['md_peak']) for r in hold),default=0),gameplay=scene['latched_gameplay']);print(label,cases[label]['music'],cases[label]['hold_native_peak'],cases[label]['hold_md_peak'],flush=True)
 old=cases[f'{level}-old-native'];native=cases[f'{level}-native'];md=cases[f'{level}-md'];nd=cases[f'{level}-native-death']
 checks[f'{level}/native_preserved']=all(old[k]==native[k] for k in ('guest','window_sha256','audio_sha256'))
 checks[f'{level}/death_then_retry']=430 in md['music'] and md['music'][-1]==track and md['gameplay']['health']>0
 checks[f'{level}/no_native_overlap']=md['hold_native_peak']==0 and md['hold_md_peak']>0
 checks[f'{level}/native_death_independent']=430 not in nd['music'] and 0 in nd['music'] and nd['music'][-1]==track and nd['hold_native_peak']>0
 checks[f'{level}/audio_guest_independent']=md['guest']==nd['guest']
paths=[Path(__file__),ROOT/'build/hakuna842/build-report.json',ROOT/'build/hakuna834-death/report.json',ROOT/'build/hakuna844-deaths/report.json',ROOT/'build/hakuna845-adult/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
