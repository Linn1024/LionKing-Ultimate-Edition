"""Compare the actual prepared-cache Be Prepared C sampler to original VDP output."""
import json,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/be-prepared867-sampler';out.mkdir(exist_ok=True);bp=ROOT/'build/be-prepared866/build-report.json';b=bound(bp);cwd=ROOT/'build/pride-sprite-fresh44'
src=out/'probe.c';src.write_text('''#include "tlk_md_assets.h"
#include <stdio.h>
int main(int argc,char **argv){
 if(argc!=4)return 2;unsigned char h[112];FILE *f=fopen(argv[1],"rb");if(!f)return 3;
 int ok=fread(h,1,112,f)==112;fclose(f);if(!ok)return 4;
 if(!TlkMdAssetsLoadCache(argv[1],h+16,h+48)||!TlkMdSceneBackgroundReady(7))return 5;
 int cx=0;sscanf(argv[2],"%d",&cx);f=fopen(argv[3],"wb");if(!f)return 6;
 for(int y=0;y<224;y++)for(int x=0;x<320;x++){
  unsigned p=TlkMdSceneBackgroundViewPixel(7,cx,0,x,y,320);fputc(p&255,f);fputc(p>>8,f);
 }fclose(f);return 0;
}
''');cmd=b['compiles']['assets'].copy();obj=out/'probe.obj'
for flag,value in (('-c',src),('-o',obj),('-MT',obj),('-MF',out/'probe.d')):cmd[cmd.index(flag)+1]=str(value)
subprocess.run(cmd,cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
objs=[str(obj),b['compiles']['assets'][b['compiles']['assets'].index('-o')+1],b['compiles']['contacts'][b['compiles']['contacts'].index('-o')+1],str(next(ROOT/p for p in b['link_inputs_sha256'] if p.replace('\\','/').endswith('/sha256.c.obj')))]
subprocess.run(['C:/mingw32/bin/gcc.exe',*objs,'-o',str(out/'probe.exe')],cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
r=bound(ROOT/'build/be-prepared864-background/report.json');cache=ROOT/'build/hakuna787-helper/scenes.cache';cases=[]
for row in r['cases']:
 field=row['field'];v=(ROOT/f'build/next824-reference/{field}-VRAM.bin').read_bytes();target=out/f'{field}.bin';subprocess.run([str(out/'probe.exe'),str(cache),str(row['displayed_camera_x']),str(target)],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW);expected=[]
 for y in range(224):
  for x in range(320):
   wx=(x-row['background_scroll'])&511;word=struct.unpack_from('>H',v,0xc000+(y//8*64+wx//8)*2)[0];px=wx&7;py=y&7
   if word&0x800:px=7-px
   if word&0x1000:py=7-py
   pixel=(v[(word&2047)*32+py*4+px//2]>>(0 if px&1 else 4))&15
   expected.append((((11 if word&0x8000 else 7)<<12)|0x900|((word>>13)&3)*16|pixel) if pixel else 0)
 actual=struct.unpack('<'+'H'*len(expected),target.read_bytes());cases.append(dict(field=field,pixels=len(expected),pixel_errors=sum(a!=z for a,z in zip(actual,expected))))
checks=dict(prepared_import_only=True,all_original_pixels=all(r['pixel_errors']==0 for r in cases));paths=[Path(__file__),bp,src,ROOT/'build/be-prepared864-background/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,sum(r['pixels'] for r in cases),'pixels',flush=True)
