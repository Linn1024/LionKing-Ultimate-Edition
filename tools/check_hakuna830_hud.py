"""Verify adult/cub HUD selection against actual original tile uploads and clients."""
import json,os,re,subprocess
from pathlib import Path
from PIL import Image,ImageChops
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna830-hud';out.mkdir(exist_ok=True);cases={};checks={};base=json.loads((ROOT/'build/hakuna816-actors/report.json').read_text())['cases']['6-native']['command'];env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
i=base.index('--input-polled');del base[i:i+2]
for name,old,extra in [('old-native',True,''),('native',False,''),('lives',False,'graphics.hud.frames.lives = md\n'),('all-hud',False,'graphics.hud.frames = md\n')]:
 folder=out/name;folder.mkdir(exist_ok=True);cmd=base.copy();cmd[0]=str(ROOT/('build/hakuna823/player.exe' if old else 'build/hakuna829/player.exe'))
 for flag,value in (('--load',ROOT/'build/hakuna796-simba/6.native.state'),('--sprite-assets',ROOT/'build/hakuna822-helper/sprites.assets'),('--frames',38120),('--hash-at',38120),('--config',folder/'host.ini'),('--resource-profile',folder/'resources.ini'),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')):cmd[cmd.index(flag)+1]=str(value)
 (folder/'host.ini').write_text('opengl = 0\nscale = 1\n');(folder/'resources.ini').write_text((ROOT/'build/hakuna816-actors/6-native/resources.ini').read_text()+'\n'+extra)
 with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
 cases[name]=dict(command=cmd,guest=dict(re.findall(r'^(frame_sha256|wram_sha256)=(\w+)',(folder/'run.log').read_text(),re.M)))
m=(ROOT/'Lion King, The (World).md').read_bytes();v5=(ROOT/'build/hakuna780-reference/28000-VRAM.bin').read_bytes();v6=(ROOT/'build/hakuna780-reference/38000-VRAM.bin').read_bytes();imgs={n:Image.open(out/n/'window.png').convert('RGB') for n in cases}
checks=dict(actual_cub_upload=v5.find(m[0x8f1f8:0x8f318])==0xd440,actual_adult_upload=v6.find(m[0x8f318:0x8f438])==0xd440,adult_upload_distinct=m[0x8f1f8:0x8f318]!=m[0x8f318:0x8f438],native_preserved=ImageChops.difference(imgs['old-native'],imgs['native']).getbbox() is None,guest_preserved=len({tuple(sorted(c['guest'].items())) for c in cases.values()})==1,lives_art_visible=ImageChops.difference(imgs['native'],imgs['lives']).getbbox() is not None,all_hud_visible=ImageChops.difference(imgs['native'],imgs['all-hud']).getbbox() is not None)
delta=ImageChops.difference(imgs['native'],imgs['lives']);delta.paste((0,0,0),(0,176,88,224));checks['life_choice_only_lives']=delta.getbbox() is None
paths=[Path(__file__),ROOT/'build/hakuna829/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
