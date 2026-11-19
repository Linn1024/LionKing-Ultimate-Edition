"""Trace Mixed Graphics HUD composition on the ordinary hyena approach."""
import json,os,re,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/level-caption349';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/hyena-hud354';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
cmd=b['compiles']['wide'].copy();cmd[cmd.index('-c')]='-E'
for flag,value in (('-o',out/'wide-original.i'),('-MT',out/'wide.obj'),('-MF',out/'wide.d')):cmd[cmd.index(flag)+1]=str(value)
with (out/'preprocess.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
text=(out/'wide-original.i').read_text();text,n=re.subn(r'TlkWideDraw\(uint32_t \*out,int width,',r'HudPreviousWideDraw354(uint32_t *out,int width,',text);assert n==1,n
text+='''
_Bool TlkWideDraw(uint32_t *out,int width,_Bool hud) {
    _Bool result=HudPreviousWideDraw354(out,width,hud);
    if(result && snes_frame_counter>=3500) {
        static FILE *f;if(!f) {f=fopen("C:/TEMP2/lionKing/build/hyena-hud354/layout.csv","w");if(!f)exit(124);
            fputs("field,width,hud,stage,fallback,column,descriptor,camera_x,camera_y,bgmode,bgchr,bgsc,mosaic,tm,ts,pieces,hud_end,roar,health\\n",f);}
        unsigned meters[2]={0};
        for(unsigned n=0;n<s_frame.piece_count;n++) {int k=HudMeter(&s_frame.pieces[n]);if(k>=0 && k<2)meters[k]++;}
        const Line *l=&s_frame.lines[24];
        fprintf(f,"%u,%d,%u,%u,%u,%d,%x,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\\n",(unsigned)snes_frame_counter,width,hud,s_frame.stage,s_stats.fallback_lines,s_stats.column,
            rd16(s_frame.ram+0xdf),rd16(s_frame.ram+0xb29b),rd16(s_frame.ram+0xb29d),l->bgmode,l->bgchr,l->bgsc[0],l->mosaic,l->tm,l->ts,s_frame.piece_count,s_frame.hud_end,meters[0],meters[1]);fflush(f);
    }
    return result;
}
'''
(out/'wide.i').write_text(text);cmd=b['compiles']['wide'].copy()
for flag,value in (('-c',out/'wide.i'),('-o',out/'wide.obj'),('-MT',out/'wide.obj'),('-MF',out/'wide.d')):cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];old=Path(b['compiles']['wide'][b['compiles']['wide'].index('-o')+1]);matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(matches)==1;inputs[matches[0]]=(out/'wide.obj').as_posix()
(out/'link.rsp').write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(out/'link.rsp'),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
ref=json.loads((ROOT/'build/pride-battle320/report.json').read_text());cmd=ref['commands']['md-new'].copy();cmd[0]=str(out/'player.exe')
for flag,n in (('--save-at',3),('--wav',2)):
    i=cmd.index(flag);del cmd[i:i+n]
for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
    (out/name).write_bytes((ROOT/'settings/mixed-graphics'/('game.ini' if flag=='--config' else 'resources.ini')).read_bytes());cmd[cmd.index(flag)+1]=str(out/name)
cmd[cmd.index('--frames')+1]='4350';cmd[cmd.index('--hash-at')+1]='3700,3800,3900,4000,4100,4200,4300'
for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json')):cmd[cmd.index(flag)+1]=str(out/name)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
with (out/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
paths=[Path(__file__),bp,out/'wide.i',out/'wide-original.i',ROOT/'settings/mixed-graphics/resources.ini']
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED' if rc==0 else 'FAIL',command=cmd,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('exit',rc,flush=True)
