"""Verify added gorilla assets/palettes without changing previous installed data."""
import csv,json,struct,subprocess,os
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_sprite_catalog import md_frame,bitmap
from pride_arena_history import bound
out=ROOT/'build/hakuna804-prepared';out.mkdir(exist_ok=True)
def package(path):
 d=path.read_bytes();count=struct.unpack_from('<I',d,20)[0];at=192+416+17792;images={}
 for _ in range(count):
  p,n,k=struct.unpack_from('<III',d,at);at+=12;images[p]=(d[at:at+n],d[at+n:at+n+k]);at+=n+k
 aggregate=d[at:];sizes=struct.unpack_from('<6I',aggregate,16);sections=[];p=40
 for n in sizes:sections.append(aggregate[p:p+n]);p+=n
 assert p==len(aggregate)
 return d,images,sections
old,oi,og=package(ROOT/'build/next741-helper/sprites.assets');new,ni,ng=package(ROOT/'build/hakuna801-helper/sprites.assets');m=(ROOT/'Lion King, The (World).md').read_bytes();pairs=json.loads((ROOT/'tools/hakuna_gorilla_pairs.json').read_text())['pairs'];original=True
for r in pairs:
 p=int(r['snes'],16)&0x3fffff;q=int(r['md'],16);b=bitmap(m,md_frame(m,q),True,with_origin=True);original &= ni[p][0]==b[4]
late=ng[5];words=struct.unpack_from('<896H',late,16);native_rows=list(csv.DictReader((ROOT/'build/hakuna781-native/poses.csv').open()));palettes=True
for r in native_rows:
 level=5 if int(r['frame'])<36500 else 6;bank=int(r['palette']);expected=words[640+(level-5)*128+bank*16:640+(level-5)*128+(bank+1)*16]
 if r['descriptor']=='c58a7f' or (level==6 and bank in (2,5,7)):
  colors=tuple(int(r['colors'][i:i+4],16) for i in range(0,64,4));palettes &= colors==expected
cmd=json.loads((ROOT/'build/hakuna803-gorilla/report.json').read_text())['cases']['both']['command'].copy();cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/next741-helper/sprites.assets');cmd[cmd.index('--dump-window')+1]=str(out/'rejected.png');cmd[cmd.index('--dump-scene')+1]=str(out/'rejected.json')
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
with (out/'old-package.log').open('wb') as log:failed=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
text=(out/'old-package.log').read_text()
checks=dict(images1063=len(ni)==1063,old_images_preserved=all(ni[k]==v for k,v in oi.items()),old_shared_palettes_and_death_bank=old[192:192+416+17792]==new[192:192+416+17792],first_five_gameplay_sections_preserved=og[:5]==ng[:5],old_next_scene_colors_preserved=og[5][16:]==late[16:16+1024],all_gorilla_images_original=bool(original),normal_actor_palettes_match=bool(palettes),next_record_v2=late[:8]==b'TLKNXT02' and len(late)==1808,old_package_rejected=failed.returncode!=0 and ('sprite' in text.lower()) and ('outdated' in text.lower() or 'incompatible' in text.lower()))
paths=[Path(__file__),ROOT/'build/hakuna801-helper/build-report.json',ROOT/'build/hakuna802/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,old_package_command=cmd,new_asset_sha256=digest(ROOT/'build/hakuna801-helper/sprites.assets'),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
