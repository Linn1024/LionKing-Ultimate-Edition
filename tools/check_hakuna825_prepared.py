"""Check current prepared actor pixels, shared-bank guard and legacy payloads."""
import json,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_sprite_catalog import md_frame,bitmap
from pride_arena_history import bound
out=ROOT/'build/hakuna825-prepared';out.mkdir(exist_ok=True);b=bound(ROOT/'build/hakuna823/build-report.json');helper=ROOT/'build/hakuna822-helper/build';cache=ROOT/'build/hakuna822-helper/sprites.assets';m=(ROOT/'Lion King, The (World).md').read_bytes()
src=out/'probe.c';src.write_text('''#include "tlk_md_sprites.h"
#include "tlk_md_sprite_assets.h"
#include "tlk_next_scene_data.h"
#include <stdio.h>
#include <string.h>
int main(int argc,char **argv){
 if(argc!=5 || !TlkMdSpriteAssetsReadFile(argv[1]) || !TlkMdSpriteAssetsActivate())return 2;
 FILE *in=fopen(argv[2],"r"),*out=fopen(argv[3],"wb");if(!in || !out)return 3;
 unsigned pose,level,bank;int bx,by,w,h;unsigned short colors[256]={0};
 while(fscanf(in,"%x %u %u %d %d %d %d",&pose,&level,&bank,&bx,&by,&w,&h)==7){
  memset(colors,0,sizeof colors);TlkMdSpritesNextScene(level);
  for(unsigned b=0;b<8;b++){const unsigned short *p=TlkNextSceneNativeObj(level,b);if(p)memcpy(colors+128+b*16,p,32);}
  if(!TlkMdSpritesDrawRole(pose,bank))return 4;
  for(int y=by;y<by+h;y++)for(int x=bx;x<bx+w;x++){
   unsigned short c=0;int r=TlkMdSpritesNpcSample(pose,x,y,0,1,1,colors,&c);if(r<0)return 5;
   unsigned v=r?c:0x8000;fputc(v&255,out);fputc(v>>8,out);
  }
 }fclose(in);fclose(out);
 /* Frog death reuses an established effect drawing in native bank5. */
 TlkMdSpritesNextScene(5);memset(colors,0,sizeof colors);memcpy(colors+208,TlkNextSceneNativeObj(5,5),32);
 pose=0xc2f35f;if(TlkMdSpritesDrawRole(pose,5)!=TLK_MD_SPRITE_DEFEAT_PUFF)return 6;
 if(!TlkMdSpritesBounds(pose,&bx,&by,&w,&h))return 7;
 int found=0,sx=0,sy=0;unsigned short c=0;
 for(int y=by;y<by+h && !found;y++)for(int x=bx;x<bx+w;x++)if(TlkMdSpritesNpcSampleBank(pose,x,y,0,1,1,5,colors,&c)==1){found=1;sx=x;sy=y;break;}
 if(!found)return 8;colors[209]^=1;
 if(TlkMdSpritesNpcSampleBank(pose,sx,sy,0,1,1,5,colors,&c)!=-1)return 9;
 TlkMdSpritesNextScene(0);if(TlkMdSpritesDrawRole(pose,5))return 10;
 if(TlkMdSpritesNpcSampleBank(pose,sx,sy,0,1,1,5,colors,&c)!=-1)return 11;
 FILE *ok=fopen(argv[4],"w");if(!ok)return 12;fputs("shared-bank and flash guards pass",ok);fclose(ok);return 0;
}
''')
cmd=['C:/mingw32/bin/gcc.exe','-std=c11','-O2','-I'+str(ROOT/'engine/runner'),'-c',str(src),'-o',str(out/'probe.obj')];subprocess.run(cmd,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=helper));objects=[]
for r in rows:
 name=r.get('file','').replace('\\','/')
 if name.endswith(('/prepare_sprite_assets.c','/tlk_md_sprite_prepare.c')):continue
 if r.get('output','').endswith('.obj'):objects.append(str(helper/r['output']))
objects.append(b['compiles']['sprites'][b['compiles']['sprites'].index('-o')+1]);subprocess.run(['C:/mingw32/bin/gcc.exe','-static',str(out/'probe.obj'),*objects,'-o',str(out/'probe.exe')],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
spec=json.loads((ROOT/'tools/hakuna_destiny_actor_pairs.json').read_text())['pairs'];gorilla=json.loads((ROOT/'tools/hakuna_gorilla_pairs.json').read_text())['pairs'];lines=[];expected=[]
def color(c):
 v=[((c>>sh)&7)*4+(((c>>sh)&7)>>2) for sh in (1,5,9)];return v[0]|v[1]<<5|v[2]<<10
for r in gorilla+spec:
 p=int(r['snes'],16);q=int(r['md'],16);level=r.get('owners',[{'level':5}])[0]['level'];bank=r.get('native_palette',6);mb=r.get('md_palette',3);x,y,w,h,pix=bitmap(m,md_frame(m,q),True,with_origin=True);lines.append(f'{p:x} {level} {bank} {x} {y} {w} {h}')
 pal=int.from_bytes(m[0x1cfdb4+level*48+44:0x1cfdb4+level*48+48],'big')+mb*32;colors=[color(int.from_bytes(m[pal+i*2:pal+i*2+2],'big')) for i in range(16)];expected += [colors[v] if v else 0x8000 for v in pix]
(out/'poses.txt').write_text('\n'.join(lines)+'\n');subprocess.run([str(out/'probe.exe'),str(cache),str(out/'poses.txt'),str(out/'pixels.bin'),str(out/'guards.txt')],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
actual=(out/'pixels.bin').read_bytes();checks=dict(all_original_pixels=actual==struct.pack('<'+'H'*len(expected),*expected),shared_bank_and_flash_guards=(out/'guards.txt').exists())
def unpack(path):
 data=path.read_bytes();n=struct.unpack_from('<I',data,20)[0];at=192+416+17792;images={}
 for _ in range(n):p,a,z=struct.unpack_from('<III',data,at);at+=12;images[p]=data[at:at+a+z];at+=a+z
 return data,images,data[at:]
old,oi,og=unpack(ROOT/'build/hakuna801-helper/sprites.assets');new,ni,ng=unpack(cache);changed={int(r['snes'],16)&0x3fffff for r in spec+gorilla}
checks.update(unrelated_images_preserved=all(ni[k]==v for k,v in oi.items() if k not in changed),all_gameplay_and_palettes_preserved=og==ng,shared_palettes_and_death_bank_preserved=old[192:18400]==new[192:18400],images1153=len(ni)==1153)
paths=[Path(__file__),src,ROOT/'build/hakuna823/build-report.json',ROOT/'build/hakuna822-helper/build-report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,poses=len(lines),pixels=len(expected),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,'poses',len(lines),'pixels',len(expected),flush=True)
