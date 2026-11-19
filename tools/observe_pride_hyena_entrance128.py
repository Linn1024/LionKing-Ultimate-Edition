"""Read-only live LLE camera-helper ABI before implementing its entrance-width source."""
import csv
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

base=ROOT/'build/pride-resource-tree118';bp=base/'build-report.json';b=bound(bp)
reference=ROOT/'build/pride-hyena-probe103/fights104/report.json';ref=bound(reference)
out=ROOT/'build/pride-hyena-entrance128';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
cmd=b['compiles']['host'].copy();cmd[cmd.index('-c')]='-E'
for flag,value in [('-o',out/'host-original.i'),('-MT',out/'host.obj'),('-MF',out/'host.d')]:cmd[cmd.index(flag)+1]=str(value)
with (out/'preprocess.log').open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
text=(out/'host-original.i').read_text();anchor='_Bool __wrap_RtlRunFrame(uint32 inputs) {';assert text.count(anchor)==1
text=text.replace(anchor,'static _Bool EntrancePreviousFrame(uint32 inputs) {')
text+='''
static unsigned EntranceWord128(unsigned at){return g_ram[at]|(unsigned)g_ram[at+1]<<8;}
static unsigned EntrancePointer128(unsigned at){return EntranceWord128(at)|(unsigned)g_ram[at+2]<<16;}
static void EntranceContext128(CpuState *cpu,uint32_t pc){
    unsigned actor=EntranceWord128(0x68),sp=cpu->S;
    if(EntranceWord128(0x1ff9e) || actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       EntrancePointer128(actor+4)!=0xc58c68 || EntrancePointer128(actor+0x30)!=0xc143ae)return;
    const char *path=getenv("TLK_ENTRANCE_CONTEXT");static FILE *f;
    if(!path)return;
    if(!f){f=fopen(path,"w");if(f)fputs("field,pc,pb,db,d,sp,a,m,x,carry,decimal,actor,scene,outer,caller,margin_x,margin_y,scratch,camera,camera_x,cached_camera_x,timer\\n",f);}
    if(f){fprintf(f,"%u,%06x,%02x,%02x,%04x,%04x,%u,%u,%u,%u,%u,%04x,%06x,%04x,%06x,%u,%u,%04x,%04x,%u,%u,%u\\n",(unsigned)snes_frame_counter+1,pc,cpu->PB,cpu->DB,cpu->D,sp,cpu->A,cpu->m_flag,cpu->x_flag,cpu->_flag_C,cpu->_flag_D,actor,EntrancePointer128(0xdf),EntranceWord128(sp+1),EntrancePointer128(sp+4),EntranceWord128(sp+7),EntranceWord128(sp+9),EntranceWord128(0xa68c),EntranceWord128(0xaa),EntranceWord128(EntranceWord128(0xaa)+8),EntranceWord128(cpu->D+0x28),EntranceWord128(actor+0x2c));fflush(f);}
}
_Bool __wrap_RtlRunFrame(uint32 inputs){
    interp_bridge_add_pre_opcode_hook(0xc03bdb,EntranceContext128);
    return EntrancePreviousFrame(inputs);
}
'''
(out/'host.i').write_text(text);cmd=b['compiles']['host'].copy();old=Path(cmd[cmd.index('-o')+1])
for flag,value in [('-c',out/'host.i'),('-o',out/'host.obj'),('-MT',out/'host.obj'),('-MF',out/'observer.d')]:cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(matches)==1
inputs[matches[0]]=(out/'host.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
cmd=ref['commands']['native'].copy();cmd[0]=str(out/'player.exe');cmd+=['--lle']
for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
    (out/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(out/file)
for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_ENTRANCE_CONTEXT=str(out/'contexts.csv'))
with (out/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
rows=list(csv.DictReader((out/'contexts.csv').open()));selected=[r for r in rows if r['caller']=='c14480']
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda p:re.findall(pattern,p.read_text())
checks=dict(exit=rc==0,all4320_native_guest_fields_preserved=hashes(out/'run.log')==hashes(reference.parent/'native/run.log'),actual_entrance_context_observed=bool(selected),
    actual_scratch_and_caller_abi=all(int(r['d'],16)==int(r['outer'],16)+0x22 and int(r['scratch'],16)==int(r['d'],16)+0x2e and r['margin_x']==r['margin_y']=='64' for r in selected),
    actual_camera_and_cpu_seam=all(r['pc']=='c03bdb' and r['pb']=='c0' and r['db']=='7e' and r['m']==r['x']==r['carry']==r['decimal']=='0' and r['a']==r['camera_x']==r['cached_camera_x'] and r['camera']=='b293' for r in selected))
paths=[Path(__file__),bp,reference,rsp,out/'host.i',out/'host-original.i',base/'genesis_plus_gx_libretro.dll']
(out/'report.json').write_text(json.dumps(dict(result='ORIGINAL_ENTRANCE_ABI_OBSERVED' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,selected_context_count=len(selected),examples=selected[:3],
    scope='Read-only current118 native LLE entrance-helper context; unchanged game objects and all4320 native guest fields. This observes the exact site/ABI for the future width adapter, not an enabled feature.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('Entrance ABI',checks,len(selected),'contexts',selected[:1],flush=True)
