"""Read-only current-player full-RAM sampling for the longer contact protocols."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
assert bound(base/'bindings/report.json')['result']=='PASS'
out=ROOT/'build/pride-contact166-observer';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
cmd=b['compiles']['host'].copy();cmd[cmd.index('-c')]='-E'
for flag,value in [('-o',out/'host-original.i'),('-MT',out/'host.obj'),('-MF',out/'host.d')]:cmd[cmd.index(flag)+1]=str(value)
with (out/'preprocess.log').open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
source=(out/'host-original.i').read_text();anchor='_Bool __wrap_RtlRunFrame(uint32 inputs) {';assert source.count(anchor)==1
source=source.replace(anchor,'static _Bool ContactPrevious166(uint32 inputs) {')
source+='''
_Bool __wrap_RtlRunFrame(uint32 inputs){
    _Bool result=ContactPrevious166(inputs);
    const char *path=getenv("TLK_CONTACT_RAM166"),*first=getenv("TLK_CONTACT_FIRST166");
    if(path && (unsigned)snes_frame_counter>=(first?(unsigned)strtoul(first,0,10):0)){
        static FILE *file;
        if(!file){file=fopen(path,"wb");if(!file)exit(116);}
        uint32_t header[4]={0x4b4c5443u,(uint32_t)snes_frame_counter,inputs,0x20000u};
        if(fwrite(header,sizeof(header),1,file)!=1 || fwrite(g_ram,0x20000u,1,file)!=1)exit(117);
        fflush(file);
    }
    return result;
}
'''
target=out/'host.i';target.write_text(source);cmd=b['compiles']['host'].copy();old=Path(cmd[cmd.index('-o')+1])
for flag,value in [('-c',target),('-o',out/'host.obj'),('-MT',out/'host.obj'),('-MF',out/'observer.d')]:cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1
inputs[indices[0]]=(out/'host.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==324 and sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==323
paths=[Path(__file__),bp,target,out/'host-original.i',rsp]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=dict(host=cmd),link_inputs_sha256=linked,nonhost_inputs_unchanged=323,
    guest_or_rom_writes_added=False,scope='Current139 host wrapper logs completed field, supplied pad and full RAM to an owned file. All game/audio/adapter objects exact. Neutrality must be checked before conclusions.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
