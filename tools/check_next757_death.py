"""Qualify Exile health-death movement/music, a current save and native retry."""
import json,os,subprocess,re,csv
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from next_level_checkpoint import native_fixture
out=ROOT/'build/next757-death';out.mkdir(exist_ok=True);base=json.loads((ROOT/'build/next756-death/report.json').read_text())['command'];cases={}
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,end,load,extra in [('continuous',25610,ROOT/'build/next756-death/entry.native.state',''),('restored',25610,out/'death.state',''),('native-motion',25610,out/'death.native.state','graphics.sprites.simba.cub.exile_death_motion = snes\n'),('native-music',25610,out/'death.native.state','audio.music.simbas_exile.death = snes\n'),('retry',26000,out/'death.state','')]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/'build/next759/player.exe')
 for flag,value in (('--load',str(load)),('--frames',str(end)),('--hash-at',str(end)),('--resource-profile',str(folder/'resources.ini')),('--config',str(folder/'host.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
 (folder/'resources.ini').write_text((ROOT/'profiles/graveyard-md.ini').read_text()+'\n'+extra);(folder/'host.ini').write_text('opengl = 0\nscale = 2\n')
 if name=='continuous':cmd+=['--save-at','25565',str(out/'death.state')]
 cmd+=['--wav',str(folder/'audio.wav'),'--wav-seconds','2']
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
 if name=='continuous':native_fixture(out/'death.state',out/'death.native.state',25565)
 scene=json.loads((folder/'scene.json').read_text());stems=list(csv.DictReader((folder/'stems.csv').open()));commands=list(csv.DictReader((folder/'commands.csv').open()))
 cases[name]=dict(command=cmd,death=scene['graveyard_death'],gameplay=scene['latched_gameplay'],window_sha256=digest(folder/'window.png'),wram_sha256=re.findall(r'wram_sha256=([a-f0-9]+)',(folder/'run.log').read_text())[-1],native_peak=max((int(r['native_peak']) for r in stems),default=0),md_peak=max((int(r['md_peak']) for r in stems),default=0),music=[r['value'] for r in commands if r['selector']=='1']);print(name,cases[name]['death'],cases[name]['native_peak'],cases[name]['md_peak'],flush=True)
c=cases;checks=dict(md_movement=c['continuous']['death']['selected']==1 and c['continuous']['death']['age']>24,native_motion_independent=c['native-motion']['death']['selected']==0 and c['native-motion']['window_sha256']!=c['continuous']['window_sha256'],presentation_guest_unchanged=c['native-motion']['wram_sha256']==c['continuous']['wram_sha256'],current_save_restore=c['restored']['window_sha256']==c['continuous']['window_sha256'],md_death_song='430' in c['continuous']['music'],no_native_music_overlap=c['restored']['native_peak']==0 and c['restored']['md_peak']>0,native_music_still_audible=c['native-music']['native_peak']>0,retry_healthy=c['retry']['gameplay']['health']>0 and c['retry']['death']['selected']==0)
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases),indent=2)+'\n');print(checks)
