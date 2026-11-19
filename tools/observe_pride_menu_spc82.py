"""Observe original menu-effect slot initialization without guest or framework edits."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-menu-audio80';bp=base/'build-report.json';prior=bound(bp)
    route=base/'route/report.json';r=bound(route)
    out=ROOT/'build/pride-menu-spc82';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
    matches=[row for row in rows if row.get('output','').replace('\\','/').endswith('/spc.c.obj') and (cwd/row['output']).resolve().relative_to(ROOT).as_posix() in prior['link_inputs_sha256']]
    assert len(matches)==1;row=matches[0];original=Path(row['file']);text=original.read_text()
    probe=ROOT/'tools/native_menu_spc_trace82.h'
    for anchor,extra in [('#include "apu.h"','\n#include "'+probe.as_posix()+'"'),('  uint8_t opcode = spc_readOpcode(spc);',None),('  apu_cpuWrite(spc->apu, adr, val);',None)]:
        assert text.count(anchor)==1
        if extra is not None:text=text.replace(anchor,anchor+extra)
    text=text.replace('  uint8_t opcode = spc_readOpcode(spc);','  Menu82Instruction(spc);\n  uint8_t opcode = spc_readOpcode(spc);')
    text=text.replace('  apu_cpuWrite(spc->apu, adr, val);','  Menu82Write(spc,adr,val);\n  apu_cpuWrite(spc->apu, adr, val);')
    source=out/'spc.c';source.write_text(text);cmd=argv(row['command'])
    for flag,value in [('-c',source),('-o',out/'spc.obj'),('-MT',out/'spc.obj'),('-MF',out/'spc.d')]:cmd[cmd.index(flag)+1]=str(value)
    cmd+=['-I'+str(original.parent)]
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=argv('link '+(base/'link.rsp').read_text())[1:];old=(cwd/row['output']).resolve()
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1
    inputs[indices[0]]=(out/'spc.obj').as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    assert len(linked)==322 and sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==321
    folder=out/'native';folder.mkdir();run=r['commands']['native'].copy();run[0]=str(out/'player.exe');run[run.index('--frames')+1]='900'
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
        (folder/file).write_bytes(Path(run[run.index(flag)+1]).read_bytes());run[run.index(flag)+1]=str(folder/file)
    for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:run[run.index(flag)+1]=str(folder/file)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env.update(SDL_VIDEODRIVER='dummy',TLK_MENU_SPC_TRACE=str(folder))
    with (folder/'run.log').open('wb') as log:rc=subprocess.run(run,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    actual=re.findall(pattern,(folder/'run.log').read_text());expected=re.findall(pattern,(base/'route/native/run.log').read_text())
    checks=dict(all900_guest_fields_neutral=rc==0 and len(actual)==900 and actual==[row for row in expected if int(row[0])<=900])
    with wave.open(str(folder/'audio.wav'),'rb') as sample,wave.open(str(base/'route/native/audio.wav'),'rb') as control:
        checks['whole_pcm_neutral']=sample.readframes(sample.getnframes())==control.readframes(sample.getnframes())
    checks['six_original_dispatch_snapshots']=len(list(folder.glob('dispatch-*.aram')))==6
    paths=[Path(__file__),bp,route,original,probe,source,rsp]
    report=dict(result='NEUTRAL_MENU_SPC_OBSERVER' if all(checks.values()) else 'FAIL',checks=checks,command=run,
                binary_sha256=digest(out/'player.exe'),link_inputs_sha256=linked,read_only_guest_observation=True,
                menu_output_filter_implemented=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
