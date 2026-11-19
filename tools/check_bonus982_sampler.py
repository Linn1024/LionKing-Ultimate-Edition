"""Compare prepared bonus background tokens with normal original VDP snapshots."""
import json,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/bonus982-sampler';out.mkdir(exist_ok=True);bp=ROOT/'build/bonus979/build-report.json';b=bound(bp);cwd=ROOT/'build/pride-sprite-fresh44';src=out/'probe.c';src.write_text('''#include "tlk_md_assets.h"
#include <stdio.h>
int main(int argc,char **argv){
 if(argc!=5)return 2;unsigned char h[112];FILE *f=fopen(argv[1],"rb");if(!f)return 3;
 int ok=fread(h,1,112,f)==112;fclose(f);if(!ok)return 4;
 unsigned level=0,width=0;sscanf(argv[2],"%u",&level);sscanf(argv[4],"%u",&width);
 if(!TlkMdAssetsLoadCache(argv[1],h+16,h+48)||!TlkMdSceneBackgroundReady(level))return 5;
 f=fopen(argv[3],"wb");if(!f)return 6;
 for(int y=0;y<224;y++)for(int x=0;x<(int)width;x++){
  unsigned p=TlkMdSceneBackgroundViewPixel(level,0,0,x,y,width);fputc(p&255,f);fputc(p>>8,f);
 }fclose(f);return 0;
}
''');cmd=b['compiles']['assets'].copy();obj=out/'probe.obj'
for flag,value in (('-c',src),('-o',obj),('-MT',obj),('-MF',out/'probe.d')):cmd[cmd.index(flag)+1]=str(value)
subprocess.run(cmd,cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW);objs=[str(obj),b['compiles']['assets'][b['compiles']['assets'].index('-o')+1],b['compiles']['contacts'][b['compiles']['contacts'].index('-o')+1],str(next(ROOT/p for p in b['link_inputs_sha256'] if p.replace('\\','/').endswith('/sha256.c.obj')))];subprocess.run(['C:/mingw32/bin/gcc.exe',*objs,'-o',str(out/'probe.exe')],cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
r=bound(ROOT/'build/bonus964-background/report.json');cases=[];records=[(row['level'],row['folder'],row['field'],320) for row in r['cases'] if row['phase']=='normal']+[(11,'early',13160,320),(13,'early',13160,256)]
for level,folder,field,width in records:
 v=(ROOT/f'build/bonus959-reference/{folder}/{field}-VRAM.bin').read_bytes();target=out/f'{level}-{field}-{width}.bin';subprocess.run([str(out/'probe.exe'),str(ROOT/'build/bonus980-scene-helper/scenes.cache'),str(level),str(target),str(width)],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW);expected=[]
 for y in range(224):
  for x in range(width):
   wx=x+(320-width)//2;word=struct.unpack_from('>H',v,0xc000+(y//8*64+wx//8)*2)[0];px=wx&7;py=y&7
   if word&0x800:px=7-px
   if word&0x1000:py=7-py
   pixel=(v[(word&2047)*32+py*4+px//2]>>(0 if px&1 else 4))&15
   expected.append((((11 if word&0x8000 else 7)<<12)|0x900|((word>>13)&3)*16|pixel) if pixel else 0)
 actual=struct.unpack('<'+'H'*len(expected),target.read_bytes());cases.append(dict(level=level,field=field,width=width,pixels=len(expected),pixel_errors=sum(a!=z for a,z in zip(actual,expected)),reference='identical Hunt source/init proof' if level==11 else 'actual original VDP'))
checks=dict(prepared_import_only=True,all_original_pixels=all(r['pixel_errors']==0 for r in cases));paths=[Path(__file__),bp,src,ROOT/'build/bonus964-background/report.json'];(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,sum(r['pixels'] for r in cases),'pixels',flush=True)
