"""Read-only all-source entrance context logging, retaining the production adapter."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride-hyena-entrance149-observer';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
module=ROOT/'engine/runner/tlk_hyena_entrance.c';source=module.read_text()
anchor='    if(!TlkResourcesUseMd("gameplay.levels.pride_lands.hyena_entrance_window"))return;'
assert source.count(anchor)==1
observer='''    {
        const char *context_path=getenv("TLK_ENTRANCE_CONTEXT149");static FILE *context;
        if(context_path){
            if(!context){context=fopen(context_path,"w");if(context)fputs("field,actor,x,y,camera_x,camera_y,player_x,player_y,timer,selected\\n",context);}
            if(context){fprintf(context,"%u,%04x,%u,%u,%u,%u,%u,%u,%u,%u\\n",(unsigned)snes_frame_counter+1,actor,word(actor+8),word(actor+10),word(0xb29b),word(0xb29d),word(0xb21b),word(0xb21d),word(actor+0x2c),TlkResourcesUseMd("gameplay.levels.pride_lands.hyena_entrance_window"));fflush(context);}
        }
    }
'''
source=source.replace(anchor,observer+anchor);target=out/'entrance-observer.c';target.write_text(source)
cmd=b['compiles']['entrance'].copy();old=Path(cmd[cmd.index('-o')+1])
for flag,value in [('-c',target),('-o',out/'entrance.obj'),('-MT',out/'entrance.obj'),('-MF',out/'entrance.d')]:cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1
inputs[indices[0]]=(out/'entrance.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
unchanged=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert len(linked)==324 and unchanged==323
paths=[Path(__file__),bp,module,target,rsp]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compile=cmd,link_inputs_sha256=linked,unchanged_production_inputs=unchanged,
    scope='Production entrance adapter with additional host-file logging after its guards and before source selection. No guest writes added; neutrality must be verified in both sources before using observations.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT observer',digest(out/'player.exe'),flush=True)
