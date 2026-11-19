"""Verify scene-v3 import using prepared buffers only and original VDP tokens."""
import json,struct,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/hakuna788-prepared';out.mkdir(exist_ok=True);b=bound(ROOT/'build/hakuna786/build-report.json');cwd=ROOT/'build/pride-sprite-fresh44'
cache=ROOT/'build/hakuna787-helper/scenes.cache';old=ROOT/json.loads((ROOT/'game-data/install.json').read_text())['scene_cache']['file'];old=ROOT/'game-data'/old.name
src=out/'probe.c';src.write_text('''#include "tlk_md_assets.h"
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char **argv){
 if(argc!=8)return 2;unsigned char header[112];FILE *f=fopen(argv[1],"rb");if(!f)return 3;
 int ok=fread(header,1,112,f)==112;fclose(f);if(!ok)return 4;
 ok=TlkMdAssetsLoadCache(argv[1],header+16,header+48);
 if(atoi(argv[7]))return ok?5:0;
 if(!ok || !TlkMdSceneBackgroundReady(5) || !TlkMdSceneBackgroundReady(6))return 6;
 unsigned level=atoi(argv[2]);TlkMdSceneAnimationPhase(level,atoi(argv[5]));
 f=fopen(argv[6],"wb");if(!f)return 7;
 for(int y=0;y<224;y++)for(int x=0;x<320;x++){
  unsigned v=TlkMdSceneBackgroundViewPixel(level,atoi(argv[3]),atoi(argv[4]),x,y,320);
  fputc(v&255,f);fputc(v>>8,f);
 }fclose(f);return 0;
}
''')
cmd=b['compiles']['assets'].copy();obj=out/'probe.obj'
for flag,value in (('-c',src),('-o',obj),('-MT',obj),('-MF',out/'probe.d')):cmd[cmd.index(flag)+1]=str(value)
subprocess.run(cmd,cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
objs=[str(obj),b['compiles']['assets'][b['compiles']['assets'].index('-o')+1],b['compiles']['contacts'][b['compiles']['contacts'].index('-o')+1],str(next(ROOT/p for p in b['link_inputs_sha256'] if p.replace('\\','/').endswith('/sha256.c.obj')))]
subprocess.run(['C:/mingw32/bin/gcc.exe',*objs,'-o',str(out/'probe.exe')],cwd=cwd,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
subprocess.run([str(out/'probe.exe'),str(old),'5','0','0','0',str(out/'unused.bin'),'1'],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
cases=[]
for row in bound(ROOT/'build/hakuna783-planes/report.json')['cases']:
 f=row['field'];target=out/f'{f}.bin';cmd=[str(out/'probe.exe'),str(cache),str(row['level']),*map(str,row['camera']),str(row['animation_phase']),str(target),'0']
 subprocess.run(cmd,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 cases.append(dict(field=f,level=row['level'],pixels=row['pixels'],matches_original=target.read_bytes()==(ROOT/f'build/hakuna783-planes/{f}.bin').read_bytes()))
def parts(path):
 d=path.read_bytes();p=120;rows=[]
 for _ in range(14):
  start=p;p+=48+128
  for _ in range(10):n=struct.unpack_from('<I',d,p)[0];p+=4+n
  rows.append(d[start:p])
 return rows,d[p:]
a,tail=parts(old);z,newtail=parts(cache)
checks=dict(scene_v3=struct.unpack_from('<I',cache.read_bytes(),8)[0]==3,only_hakuna_payload_changes=all(a[i]==z[i] for i in range(14) if i!=5),gameplay_palette_recipes_preserved=tail==newtail,old_v2_rejected=True,all_original_samples=all(c['matches_original'] for c in cases))
paths=[Path(__file__),src,ROOT/'build/hakuna786/build-report.json',ROOT/'build/hakuna787-helper/build-report.json',ROOT/'build/hakuna783-planes/report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,cache_sha256=digest(cache),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)
