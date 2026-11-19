"""Read-only tracked-field observer for maintained226, no preprocessor copies."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from build_pride_rng_allbugs import OBSERVER
from pride_arena_history import bound
base=ROOT/'build/pride-menu226-integrated';bp=base/'build-report.json';b=bound(bp)
assert shutil.disk_usage(ROOT).free>64*1024*1024,'Need64MB headroom before linking observer'
out=base/'allbugs-observer';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
cmd=b['compiles']['host'].copy();cmd[cmd.index('-c')]='-E'
for flag,value in [('-o','-'),('-MF',out/'preprocess.d'),('-MT',out/'host.obj')]:cmd[cmd.index(flag)+1]=str(value)
with (out/'preprocess.log').open('wb') as f:original=subprocess.check_output(cmd,cwd=cwd,stderr=f)
s=original.decode();anchor='_Bool __wrap_RtlRunFrame(uint32 inputs) {';assert s.count(anchor)==1
s=s.replace(anchor,'static _Bool MenuObservedPrevious238(uint32 inputs) {')+'\n'+OBSERVER.replace('PrideObservedRunFrame(inputs)','MenuObservedPrevious238(inputs)')
cmd=b['compiles']['host'].copy();old=(cwd/Path(cmd[cmd.index('-o')+1])).resolve()
for flag,value in [('-c','-'),('-o',out/'host.obj'),('-MF',out/'host.d'),('-MT',out/'host.obj')]:cmd[cmd.index(flag)+1]=str(value)
cmd[cmd.index('-c'):cmd.index('-c')]=['-x','cpp-output']
with (out/'compile.log').open('wb') as f:subprocess.run(cmd,input=s.encode(),cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1
inputs[indices[0]]=(out/'host.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as f:subprocess.run(['C:/mingw32/bin/g++.exe','-s','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
assert len(linked)==324 and sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==323
paths=[Path(__file__),bp,rsp,ROOT/'tools/build_pride_rng_allbugs.py',ROOT/'engine/runner/pride/final/pride_final_host.c',*sorted((ROOT/'engine/runner/pride/final').glob('*.inc'))]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),link_inputs_sha256=linked,
    nonhost_inputs_unchanged=323,guest_writes_added=False,debug_symbols_stripped=True,
    original_preprocessed_sha256=hashlib.sha256(original).hexdigest(),instrumented_preprocessed_sha256=hashlib.sha256(s.encode()).hexdigest(),
    scope='Read-only original tracked-field observer around maintained226.323/324 inputs retained; stripped debug symbols, requires production pilot neutrality before full reference conclusions.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),'bytes',(out/'player.exe').stat().st_size,flush=True)
