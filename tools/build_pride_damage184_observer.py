"""Compact read-only damage/attacker fields around the unchanged139 host."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
old=ROOT/'build/pride-contact166-observer/build-report.json';bound(old)
out=ROOT/'build/pride-damage184-observer';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
pre=old.parent/'host-original.i';s=pre.read_text();anchor='_Bool __wrap_RtlRunFrame(uint32 inputs) {';assert s.count(anchor)==1
s=s.replace(anchor,'static _Bool DamagePrevious184(uint32 inputs) {')
s+='''
static unsigned DamageWord184(unsigned at){return g_ram[at]|(unsigned)g_ram[at+1]<<8;}
static unsigned DamagePointer184(unsigned at){return DamageWord184(at)|(unsigned)g_ram[at+2]<<16;}
_Bool __wrap_RtlRunFrame(uint32 inputs){
    _Bool result=DamagePrevious184(inputs);
    const char *path=getenv("TLK_DAMAGE184"),*begin=getenv("TLK_DAMAGE_FIRST184");
    if(path && (unsigned)snes_frame_counter>=(begin?(unsigned)strtoul(begin,0,10):0)){
        static FILE *file;
        if(!file){file=fopen(path,"w");if(!file)exit(118);fputs("field,pad,scene,health,spares,x,y,action,immunity,pending,attacker,attacker_descriptor,attacker_action,attacker_x,attacker_y\\n",file);}
        unsigned pointer=DamagePointer184(0xb237),at=pointer&65535;
        unsigned valid=(pointer>>16)==0x7e && at>=0xb293 && at<0xc213 && ((at-0xb213)&127)==0;
        fprintf(file,"%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\\n",(unsigned)snes_frame_counter,inputs,DamagePointer184(0xdf),DamageWord184(0x2004),DamageWord184(0x1ffaa),DamageWord184(0xb21b),DamageWord184(0xb21d),DamagePointer184(0xb243),g_ram[0xb259],g_ram[0xb256]&4,pointer,valid?DamagePointer184(at+4):0,valid?DamagePointer184(at+0x30):0,valid?DamageWord184(at+8):0,valid?DamageWord184(at+10):0);
        fflush(file);
    }
    return result;
}
'''
target=out/'host.i';target.write_text(s);cmd=b['compiles']['host'].copy();original=Path(cmd[cmd.index('-o')+1])
for flag,value in [('-c',target),('-o',out/'host.obj'),('-MT',out/'host.obj'),('-MF',out/'host.d')]:cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==original];assert len(indices)==1
inputs[indices[0]]=(out/'host.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==324 and sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==323
paths=[Path(__file__),bp,old,pre,target,rsp]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),link_inputs_sha256=linked,nonhost_inputs_unchanged=323,guest_writes_added=False,
    scope='Compact per-field current139 player/attacker logging only; no protocol or difficulty edits. Needs production neutrality validation before fidelity conclusions.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
