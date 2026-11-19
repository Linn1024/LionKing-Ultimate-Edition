"""Check the actual C Exile sampler against original VDP pixels at four cameras."""
import json,struct,subprocess,csv
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next749-background';out.mkdir(exist_ok=True);b=json.loads((ROOT/'build/next747/build-report.json').read_text())
src=out/'probe.c';src.write_text('''#include "tlk_md_assets.h"
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char **argv){
 if(argc!=4)return 2;unsigned char header[112];FILE *f=fopen(argv[1],"rb");if(!f)return 3;
 int ok=fread(header,1,112,f)==112;fclose(f);if(!ok || !TlkMdAssetsLoadCache(argv[1],header+16,header+48))return 4;
 if(!TlkMdSceneBackgroundReady(4))return 5;f=fopen(argv[3],"wb");if(!f)return 6;
 int cx=atoi(argv[2]);for(int y=0;y<224;y++)for(int x=0;x<320;x++){
  unsigned v=TlkMdSceneBackgroundViewPixel(4,cx,0,x,y,320);fputc(v&255,f);fputc(v>>8,f);
 }fclose(f);return 0;
}
''')
cwd=ROOT/'build/pride-sprite-fresh44';obj=out/'probe.obj';cmd=b['compiles']['assets'].copy()
for flag,value in (('-c',src),('-o',obj),('-MT',obj),('-MF',out/'probe.d')):cmd[cmd.index(flag)+1]=str(value)
subprocess.run(cmd,cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
objects=[]
for label in ('assets','contacts'):objects.append(b['compiles'][label][b['compiles'][label].index('-o')+1])
sha=next(ROOT/p for p in b['link_inputs_sha256'] if p.replace('\\','/').endswith('/sha256.c.obj'))
subprocess.run(['C:/mingw32/bin/gcc.exe',str(obj),*objects,str(sha),'-o',str(out/'probe.exe')],cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
base=json.loads((ROOT/'build/graveyard660-skull-audio/report.json').read_text())['commands']['death'];cache=base[base.index('--asset-cache')+1];cases=[]
for row in csv.DictReader((ROOT/'build/next726-reference/scroll.csv').open()):
 if row['level']!='4':continue
 field=int(row['field']);vram=(ROOT/f'build/next726-reference/{field}-VRAM.bin').read_bytes();pixels=[];offsets=[int(row['offsets'][i:i+4],16) for i in range(0,len(row['offsets']),4)]
 for y in range(224):
  shift=(-offsets[y])&1023
  for x in range(320):
   wx=(x+shift)&511;tile=int.from_bytes(vram[0xc000+(y//8*64+wx//8)*2:0xc002+(y//8*64+wx//8)*2],'big');xx=wx&7;yy=y&7
   if tile&0x800:xx=7-xx
   if tile&0x1000:yy=7-yy
   packed=vram[(tile&2047)*32+yy*4+xx//2];pixel=packed>>(0 if xx&1 else 4)&15
   pixels.append(((11 if tile&0x8000 else 7)<<12)|0x900|((tile>>13)&3)*16|pixel if pixel else 0)
 actual=out/f'{field}.bin';subprocess.run([str(out/'probe.exe'),cache,row['camera_x'],str(actual)],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 expected=struct.pack('<'+'H'*len(pixels),*pixels);data=actual.read_bytes();errors=sum(a!=b for a,b in zip(struct.unpack('<'+'H'*len(pixels),data),pixels));cases.append(dict(field=field,pixels=len(pixels),errors=errors));print(field,errors,flush=True)
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(c['errors']==0 for c in cases) else 'FAIL',cases=cases,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),src,ROOT/'build/next747/build-report.json',ROOT/'build/next726-reference/report.json')}),indent=2)+'\n')
