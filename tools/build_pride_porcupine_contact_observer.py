"""Build a read-only attack observer; production38 and maintained sources stay intact."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-porcupine38';old=bound(prior/'build-report.json')
    reference=ROOT/'build/pride-porcupine37/build-report.json';commands=bound(reference)
    out=ROOT/'build/pride-porcupine-contact-observer';out.mkdir();cwd=ROOT/'build/pride-final-standalone'
    original=ROOT/'engine/runner/tlk_porcupine_attack_runtime.c';text=original.read_text()
    replacements=[('#include "common_rtl.h"','#include "common_rtl.h"\n#include "snes/snes.h"'),
        (r'phase_before,phase_after,next\n',r'phase_before,phase_after,next,field,contact_result,victim,player_flags,attacker,health,player_x,player_y,actor_x,actor_y\n'),
        (r'"%06x,%04x,%u,%u,%u,%u,%u,%u,%06x\n",pc,actor,word(actor+0x2c),word(actor+0x1c),word(actor+0x22),word(actor+0x2e),before,phase,next',
         r'"%06x,%04x,%u,%u,%u,%u,%u,%u,%06x,%u,%04x,%04x,%02x,%06x,%u,%u,%u,%u,%u\n",pc,actor,word(actor+0x2c),word(actor+0x1c),word(actor+0x22),word(actor+0x2e),before,phase,next,(unsigned)snes_frame_counter+1,word(cpu->D+0x0c),word(0x6e),g_ram[0xb213+0x43],address(0xb213+0x24),word(0x2004),word(0xb213+8),word(0xb213+10),word(actor+8),word(actor+10)')]
    for before,after in replacements:
        assert text.count(before)==1,before;text=text.replace(before,after)
    source=out/'contact-observer.c';source.write_text(text)
    cmd=commands['compiles']['attack-runtime'].copy();obj=out/'observer.obj'
    for flag,value in [('-c',source),('-o',obj),('-MF',out/'observer.d'),('-MT',obj)]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:]
    previous=ROOT/'build/pride-porcupine37/attack-runtime.obj'
    index=next(i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==previous)
    inputs[index]=obj.as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','-O3','-static',
        '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine','@'+str(rsp),'-o',str(out/'player.exe')],
        cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(prior/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    paths=[Path(__file__),prior/'build-report.json',reference,original,source]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles={'observer':cmd},
                observer_only=True,maintained_source_edited=False,replacements=replacements,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                link_inputs_sha256={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-')})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
