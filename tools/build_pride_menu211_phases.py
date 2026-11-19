"""Read-only native Continue phase callbacks, compiling through stdin."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound

base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
prior=ROOT/'build/pride-menu209-observer/build-report.json';bound(prior)
out=ROOT/'build/pride-menu211-phases';out.mkdir()
cwd=ROOT/'build/pride-sprite-fresh44'
pre=prior.parent/'host.i';s=pre.read_text()
anchor='_Bool __wrap_RtlRunFrame(uint32 inputs) {'
assert s.count(anchor)==1
s=s.replace(anchor,'static _Bool MenuPrevious211(uint32 inputs) {')
s+='''
static void MenuPhase211(CpuState *cpu,uint32_t pc){
    MenuObserve197(pc==0xc08da5?"NativeExitStart":pc==0xc08da9?"NativeExitWait":"NativeReloadStart",cpu,pc);
}
_Bool __wrap_RtlRunFrame(uint32 inputs){
    static unsigned installed;
    if(!installed){
        if(!interp_bridge_add_pre_opcode_hook(0xc08da5,MenuPhase211) ||
           !interp_bridge_add_pre_opcode_hook(0xc08da9,MenuPhase211) ||
           !interp_bridge_add_pre_opcode_hook(0xc08dad,MenuPhase211))exit(122);
        installed=1;
    }
    return MenuPrevious211(inputs);
}
'''
cmd=b['compiles']['host'].copy();original=Path(cmd[cmd.index('-o')+1])
for flag,value in [('-c','-'),('-o',out/'host.obj'),('-MT',out/'host.obj'),('-MF',out/'host.d')]:cmd[cmd.index(flag)+1]=str(value)
cmd+=['-x','cpp-output']
with (out/'compile.log').open('wb') as f:
    subprocess.run(cmd,input=s.encode(),cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:]
indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==original];assert len(indices)==1
inputs[indices[0]]=(out/'host.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==324 and sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==323
paths=[Path(__file__),bp,prior,pre,rsp]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),
    link_inputs_sha256=linked,nonhost_inputs_unchanged=323,guest_writes_added=False,
    preprocessed_input_sha256=hashlib.sha256(s.encode()).hexdigest(),compilation=cmd,
    scope='Read-only existing emitted native Continue phase callbacks; stdin build avoids another large duplicate preprocessed file.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
