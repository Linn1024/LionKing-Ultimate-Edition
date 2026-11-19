"""Run an isolated original-CPU widget oracle including observed transition flag2.

Preserves the existing 0/1/3/FFFF oracle and all production objects/binaries.
These are explicit guest-value fixtures, separate from ordinary gameplay.
"""
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest


def main():
    out=ROOT/'build/pride-default-actor/font-oracle';out.mkdir(exist_ok=True)
    original=ROOT/'tools/pride_native_hud_oracle.c';source=original.read_text()
    anchor='static const uint16_t flags[]={0,1,3,65535};';assert source.count(anchor)==1
    source=source.replace(anchor,'static const uint16_t flags[]={0,1,2,65535};')
    source=source.replace('../engine/runner/headless_main.c',(ROOT/'engine/runner/headless_main.c').as_posix())
    clone=out/'original-flag2.c';clone.write_text(source)
    folder=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=folder))
    entry=next(r for r in db if 'tlk_native_hud_oracle.dir' in r.get('output','') and r['file'].endswith('pride_native_hud_oracle.c'))
    obj=out/'original-flag2.obj';command=argv(entry['command'])
    for flag,value in (('-c',clone.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
        command[command.index(flag)+1]=value
    with (out/'compile.log').open('wb') as log:
        subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    expanded=json.loads(subprocess.check_output([ninja,'-t','compdb','-x'],cwd=folder))
    link=next(r['command'] for r in expanded if r.get('output')=='tlk_native_hud_oracle.exe')
    command=argv(link.split('&&',1)[1].rsplit('&&',1)[0].strip())
    suffix=entry['output'].replace('\\','/');replaced=0
    for n,arg in enumerate(command):
        if arg.replace('\\','/')==suffix:command[n]=obj.as_posix();replaced+=1
    assert replaced==1
    inputs={}
    for arg in command:
        if not arg.startswith('-') and arg.lower().endswith(('.obj','.a')):
            p=Path(arg);p=p if p.is_absolute() else folder/p
            inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
    binary=out/'original-flag2.exe';command[command.index('-o')+1]=binary.as_posix()
    for n,arg in enumerate(command):
        if arg.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/'oracle.dll.a').as_posix()
    with (out/'link.log').open('wb') as log:
        subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    tape=out/'boot-neutral.polled.tape';tape.write_bytes((ROOT/'engine/tapes/allbugsF.read.tape').read_bytes()[:1600]+bytes(40000))
    env=os.environ.copy();env['TLK_NATIVE_HUD_PARTIAL']='1';env['TLK_NATIVE_HUD_ORACLE']=str(out/'original-fonts.bin')
    with (out/'run.log').open('wb') as log:
        subprocess.run([str(binary),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--lle','--frames','12000','--input-polled',str(tape)],
            cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    raw=(out/'original-fonts.bin').read_bytes();assert raw[:8]==b'SNHUD002' and len(raw)==8+8445*1044
    seen={}
    for at in range(8,len(raw),1044):
        kind,maximum,current,initial,last=struct.unpack_from('<5I',raw,at)
        if not kind:seen[maximum,current,initial]=raw[at+532:at+1044]
    assert set(seen)=={(m,c,f) for m in range(8,65) for c in range(m+1) for f in (0,1,2,65535)}
    for name,sha in inputs.items():assert digest(ROOT/name)==sha,name
    sources=[Path(__file__),original,clone,ROOT/'engine/runner/tlk_native_hud.c',ROOT/'engine/runner/tlk_native_hud.h']
    report=dict(result='PASS',scope=__doc__,original_roar_cases=len(seen),transition_flags=[0,1,2,65535],
        binary_sha256=digest(binary),link_inputs_sha256=inputs,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'},
        actual_gameplay=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original CPU 8436 roar fixtures including flag2 exact; predecessor oracle unchanged',flush=True)


if __name__=='__main__':main()
