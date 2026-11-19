"""Private backdrop diagnostic; never modify the maintained runtime for tracing."""
import json,shutil,subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv
out=ROOT/'build/next769-probe';out.mkdir(exist_ok=True);base=ROOT/'build/next766';b=json.loads((base/'build-report.json').read_text());cwd=ROOT/'build/pride-sprite-fresh44'
shutil.copytree(ROOT/'engine/runner',out/'runner',dirs_exist_ok=True);p=out/'runner/tlk_wide.c';s=p.read_text();a='        out[i] = (uint32_t)map[r] << 16 | (uint32_t)map[g] << 8 | map[b];';assert a in s
s=s.replace(a,'        if(y0==0 && i==width/2){static int count;if(count++<3)fprintf(stderr,"BACKDROP stage=%d pal=%d main=%x layer=%u c=%x rgb=%u,%u,%u ext0=%x cgram0=%x fixed=%x math=%x\\n",stampede,stampede_palette,main,layer,c,r,g,b,TlkNextSceneMdPalette(3)[0],l->cgram[0],l->fixed,l->cgadsub);}\n'+a);p.write_text(s)
cmd=b['compiles']['wide'].copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/'wide.obj'
for flag,value in (('-o',obj),('-MT',obj),('-MF',out/'wide.d'),('-c',out/'runner/pride/final/pride_final_wide.c')):cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];ix=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(ix)==1;inputs[ix[0]]=obj.as_posix();(out/'link.rsp').write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(out/'link.rsp'),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copyfile(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll');cmd=json.loads((ROOT/'build/next767-backdrop/report.json').read_text())['command'];cmd[0]=str(out/'player.exe');cmd+=['--no-pace'];cmd[cmd.index('--frames')+1]='2302'
with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
print((out/'run.log').read_text()[-2600:])
