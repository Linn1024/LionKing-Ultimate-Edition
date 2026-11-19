"""Final bonus music source isolation, result-card stop and native preservation."""
import json,csv,os,re,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/bonus990-audio';out.mkdir(exist_ok=True);refs=json.loads((ROOT/'build/bonus972-choices/report.json').read_text())['cases'];cases={};checks={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
def run(level,name,old=False,md=False,long=False):
 folder=out/f'{level}-{name}';folder.mkdir(exist_ok=True);cmd=refs[f'{level}-native']['command'].copy();cmd[0]=str(ROOT/('dist/installed-preview949/LionKing.exe' if old else 'build/bonus989/player.exe'));start=1700 if level==10 else 1900;end=start+(280 if long else 80)
 for flag,value in (('--frames',end),('--hash-at',end),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--sprite-assets',ROOT/('build/pride928-helper/sprites.assets' if old else 'build/bonus985-sprite-helper/sprites.assets')),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 source='bug_toss' if level==10 else 'bug_hunt';(folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text('schema = 1\ngame = snes\n'+(f'audio.music.{source} = md\n' if md else ''));cmd+=['--wav',str(folder/'audio.wav'),'--wav-seconds','6']
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
 commands=list(csv.DictReader((folder/'commands.csv').open()));stems=list(csv.DictReader((folder/'stems.csv').open()));hold=[r for r in stems if start+20<=int(r['frame'])<=start+70];tail=[r for r in stems if int(r['frame'])>=1930];scene=json.loads((folder/'scene.json').read_text());r=dict(command=cmd,music=[int(r['value']) for r in commands if r['selector']=='1'],guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)),pcm_sha256=digest(folder/'audio.wav'),native_peak=max((int(r['native_peak']) for r in hold),default=0),md_peak=max((int(r['md_peak']) for r in hold),default=0),result_card_md_peak=max((int(r['md_peak']) for r in tail),default=0),gameplay=scene['latched_gameplay']);cases[f'{level}-{name}']=r;print(level,name,r['music'],r['native_peak'],r['md_peak'],r['result_card_md_peak'],flush=True);return r
for level in (10,11,12,13):
 native=run(level,'native');md=run(level,'md',md=True);checks[f'{level}/original_track']=md['music']==[134 if level==10 else 281];checks[f'{level}/native_music_isolated']=md['md_peak']>0 and md['native_peak']==0;checks[f'{level}/gameplay_preserved']=native['gameplay']==md['gameplay']
 if level in (10,13):
  old=run(level,'old-native',old=True);checks[f'{level}/native_audio_preserved']=old['guest']==native['guest'] and old['pcm_sha256']==native['pcm_sha256']
toss=run(10,'result-card',md=True,long=True);checks['toss/result_card_stops_music']=toss['result_card_md_peak']==0
paths=[Path(__file__),ROOT/'build/bonus989/build-report.json',ROOT/'build/bonus985-sprite-helper/build-report.json',ROOT/'build/bonus959-reference/report.json'];(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
