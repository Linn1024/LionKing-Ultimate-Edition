"""Exercise observed Exile pickup owners and the selected roar branch locally."""
import json,os,subprocess,csv,re,struct
from audit_scenes import ROOT
out=ROOT/'build/next764-choices';out.mkdir(exist_ok=True)
base=json.loads((ROOT/'build/next755-exile/report.json').read_text())['cases']['md']['command'];cases={};env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
for name,end,extra in [('pickups-snes',25000,'graphics.sprites.pickups.frames = snes\ngraphics.sprites.pickups.palette = snes\n'),('pickups-md',25800,''),('roar-md',2360,'')]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/'build/next763/player.exe')
 if name=='roar-md':
  r=json.loads((ROOT/'build/next745-presentation/report.json').read_text())['cases']['4-native']['command'];cmd=r.copy();cmd[0]=str(ROOT/'build/next763/player.exe');(folder/'input.polled.tape').write_bytes(struct.pack('<'+'H'*60,*([0x80]*20+[0]*40)));cmd+=['--input-polled',str(folder/'input.polled.tape')]
 for flag,value in (('--frames',str(end)),('--hash-at','25000,25800' if name=='pickups-md' else str(end)),('--resource-profile',str(folder/'resources.ini')),('--config',str(folder/'host.ini')),('--dump-window',str(folder/'window.png')),('--dump-scene',str(folder/'scene.json'))):cmd[cmd.index(flag)+1]=value
 (folder/'host.ini').write_text('opengl = 0\nscale = 2\n');(folder/'resources.ini').write_text(('schema = 1\ngame = snes\ngameplay.simba.roar = md\n' if name=='roar-md' else (ROOT/'profiles/graveyard-md.ini').read_text()+'\n'+extra))
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=dict(env,TLK_SPRITE_REPORT=str(folder/'sprites.json'),TLK_ROAR_TRACE=str(folder/'roar.csv')),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
 s=json.loads((folder/'sprites.json').read_text());trace=list(csv.DictReader((folder/'roar.csv').open())) if (folder/'roar.csv').exists() else [];hashes=re.findall(r'frame=(\d+).*?wram_sha256=([a-f0-9]+)',(folder/'run.log').read_text(),re.S)
 cases[name]=dict(command=cmd,roles=s['seen_by_role'],hashes=hashes,roar=trace);print(name,s['seen_by_role']['pickup'],len(trace),flush=True)
checks=dict(md_pickup_artwork_exercised=cases['pickups-md']['roles']['pickup']>0,snes_pickups_independent=cases['pickups-snes']['roles']['pickup']==0,roar14=any(r['event']=='activation_delay' and r['value']=='14' for r in cases['roar-md']['roar']))
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases),indent=2)+'\n');print(checks)
