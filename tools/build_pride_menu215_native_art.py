"""Private installed MD Continue/Game Over art over native controls and fades."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
prior=ROOT/'build/pride-menu200-native-art/build-report.json';bound(prior)
out=ROOT/'build/pride-menu215-native-art';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
pre=prior.parent/'host.i';s=pre.read_text()
module=Path(__file__).with_name('pride_menu215_native_art.inc')
anchor='static void FinalSceneBegin(CpuState *cpu,uint32_t pc) {';assert s.count(anchor)==1
s=s.replace(anchor,'static int NativeMenu215Enabled(void);\nstatic void NativeMenu215Event(const char *);\nstatic void NativeMenu215Paint(uint32_t *,int);\n'+anchor)
anchor='&& !NativeMenu200Enabled()) {';assert s.count(anchor)==1
s=s.replace(anchor,'&& !NativeMenu200Enabled() && !NativeMenu215Enabled()) {')
anchor='static void MenuObserve197(const char *kind,CpuState *cpu,uint32_t pc){';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'NativeMenu215Event(kind);').replace('snes_frame_counter<4000','snes_frame_counter<3000')
for anchor,extra in [('ContinueMenuPaint(pixels,256);','NativeMenu215Paint(pixels,256);'),('ContinueMenuPaint(pixels,width);','NativeMenu215Paint(pixels,width);')]:
    assert s.count(anchor)==1;s=s.replace(anchor,anchor+extra)
s+='\n'+module.read_text()
cmd=b['compiles']['host'].copy();original=Path(cmd[cmd.index('-o')+1])
for flag,value in [('-c','-'),('-o',out/'host.obj'),('-MT',out/'host.obj'),('-MF',out/'host.d')]:cmd[cmd.index(flag)+1]=str(value)
cmd[cmd.index('-c'):cmd.index('-c')]=['-x','cpp-output']
with (out/'compile.log').open('wb') as f:subprocess.run(cmd,input=s.encode(),cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==original];assert len(indices)==1
inputs[indices[0]]=(out/'host.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==324 and sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==323
paths=[Path(__file__),module,bp,prior,pre,rsp]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),link_inputs_sha256=linked,
    nonhost_inputs_unchanged=323,guest_writes_added=False,preprocessed_input_sha256=hashlib.sha256(s.encode()).hexdigest(),
    scope='Private native-timing MD artwork, live cursor and retained credits; MD art animation program, native duration/brightness. Requires route/mode/visual verification; no public/save/source-switch claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
