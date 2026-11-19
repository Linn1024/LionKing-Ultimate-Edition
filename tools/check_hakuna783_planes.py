"""Check prepared Hakuna/Destiny plane samples against actual original VDP state.

No whole-game replay: use the nearby original captures780. The camera passed to
the sampler is the completed background callback's camera, not the next actor
position. Rendering readiness remains disabled until the native controller lands.
"""
import csv,json,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna783-planes';out.mkdir(exist_ok=True)
b=json.loads((ROOT/'build/next771/build-report.json').read_text());cwd=ROOT/'build/pride-sprite-fresh44'
src=out/'probe.c';src.write_text('''#include "tlk_md_assets.h"
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char **argv){
 if(argc!=8)return 2;FILE *f=fopen(argv[1],"rb");if(!f)return 3;
 unsigned char *rom=malloc(0x300000);if(!rom)return 4;
 if(fread(rom,1,0x300000,f)!=0x300000)return 5;fclose(f);
 if(!TlkMdAssetsInit(rom,0x300000))return 6;free(rom);
 unsigned level=atoi(argv[2]);TlkMdSceneAnimationPhase(level,atoi(argv[5]));
 f=fopen(argv[6],"wb");if(!f)return 7;
 for(int y=0;y<224;y++)for(int x=0;x<320;x++){
  unsigned v=TlkMdScenePixel(level,1,0,0,atoi(argv[3]),atoi(argv[4]),x,y,0,0,0,320);
  fputc(v&255,f);fputc(v>>8,f);
 }fclose(f);
 /* Keep all unadapted background capability claims disabled. */
 if(TlkMdSceneBackgroundReady(5) || TlkMdSceneBackgroundReady(6))return 8;
 return 0;
}
''')
objs=[]
for name,file in (('probe',src),('assets',ROOT/'engine/runner/tlk_md_assets.c')):
 cmd=b['compiles']['assets'].copy();obj=out/(name+'.obj')
 for flag,value in (('-c',file),('-o',obj),('-MT',obj),('-MF',out/(name+'.d'))):cmd[cmd.index(flag)+1]=str(value)
 subprocess.run(cmd,cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW);objs.append(str(obj))
objs.append(b['compiles']['contacts'][b['compiles']['contacts'].index('-o')+1])
objs.append(str(next(ROOT/p for p in b['link_inputs_sha256'] if p.replace('\\','/').endswith('/sha256.c.obj'))))
subprocess.run(['C:/mingw32/bin/gcc.exe',*objs,'-o',str(out/'probe.exe')],cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
m=(ROOT/'Lion King, The (World).md').read_bytes();cases=[]
for row in csv.DictReader((ROOT/'build/hakuna780-reference/scroll.csv').open()):
 field=int(row['field']);level=int(row['level']);v=(ROOT/f'build/hakuna780-reference/{field}-VRAM.bin').read_bytes();ram=(ROOT/f'build/hakuna780-reference/{field}-68K RAM.bin').read_bytes()
 vs=int(row['vsram']);table=int.from_bytes(ram[0xc60c:0xc610],'big')&65535
 # Read the completed VDP transfer, rather than RAM already updated for the
 # following field. Plane A's uniform scroll identifies the displayed camera.
 offsets=tuple(struct.unpack_from('>H',v,0xfc02+y*4)[0] for y in range(224))
 rawcx=(-struct.unpack_from('>H',v,0xfc00)[0])&1023
 cx=min((rawcx+n*1024 for n in range(8)),key=lambda x:abs(x-int(row['camera_x'])))
 cy=struct.unpack_from('>H',(ROOT/f'build/hakuna780-reference/{field}-VSRAM.bin').read_bytes(),0)[0] if level==5 else 0
 phase=next((p for p in range(4) if v[28448:28448+1440]==m[0x8c502+p*1440:0x8c502+(p+1)*1440]),None) if level==5 else 0
 assert phase is not None,(field,'unrecognized animation upload')
 pixels=[];expected_scroll=[]
 for y in range(224):
  yy=y+vs if level==5 else y
  shift=(0 if yy<8 else 3 if yy<144 else 2 if yy<240 else 1) if level==5 else (5 if y<96 else 4 if y<112 else 3 if y<144 else 2 if y<192 else 1)
  expected_scroll.append(0 if level==5 and yy<8 else (-(cx>>shift))&1023)
  for x in range(320):
   wx=(x-offsets[y])&511;wy=yy&255;word=struct.unpack_from('>H',v,0xc000+(wy//8*64+wx//8)*2)[0];xx=wx&7;py=wy&7
   if word&0x800:xx=7-xx
   if word&0x1000:py=7-py
   pixel=(v[(word&2047)*32+py*4+xx//2]>>(0 if xx&1 else 4))&15
   pixels.append((((11 if word&0x8000 else 7)<<12)|0x900|((word>>13)&3)*16|pixel) if pixel else 0)
 # Original Hakuna hardware plane is64x32;18C0 streams the visible rows from
 # a64x64 source map. Do not repeat the initial32 hardware rows vertically.
 target=out/f'{field}.bin';cmd=[str(out/'probe.exe'),str(ROOT/'Lion King, The (World).md'),str(level),str(cx),str(cy),str(phase),str(target),'reserved']
 subprocess.run(cmd,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 data=target.read_bytes();actual=struct.unpack('<'+'H'*len(pixels),data)
 r=dict(field=field,level=level,camera=[cx,cy],animation_phase=phase,pixels=len(pixels),scroll_errors=sum(a!=b for a,b in zip(expected_scroll,offsets)),pixel_errors=sum(a!=b for a,b in zip(actual,pixels)))
 cases.append(r);print(r,flush=True)
paths=[Path(__file__),ROOT/'engine/runner/tlk_md_assets.c',ROOT/'engine/runner/tlk_md_assets.h',ROOT/'build/hakuna780-reference/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(not r['pixel_errors'] and not r['scroll_errors'] for r in cases) else 'FAIL',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
