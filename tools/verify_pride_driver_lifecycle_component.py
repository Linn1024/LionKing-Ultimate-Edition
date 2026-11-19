"""Unknown-driver fallback and queue/voice invalidation on actual private code."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest

SOURCE=r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
uint8_t g_ram[131072];unsigned snes_frame_counter;
#define PrideSemanticReset PrideOriginalSemanticReset
#define PrideSemanticSpc PrideOriginalSemanticSpc
#define PrideSemanticVoice PrideOriginalSemanticVoice
#include "native_bounce_semantic_owner2.h"
#undef PrideSemanticReset
#undef PrideSemanticSpc
#undef PrideSemanticVoice
#include "native_bounce_driver_lifecycle.h"
Snes *g_snes;
static unsigned checks;
#define CHECK(v) do { assert(v);checks++; } while(0)
static void word(unsigned at,unsigned v) { g_ram[at]=v;g_ram[at+1]=v>>8; }
static void address(unsigned at,unsigned v) { word(at,v);g_ram[at+2]=v>>16; }
static void accept(CpuState *cpu) {
    cpu->D=0x1f00;cpu->DB=0x7e;cpu->m_flag=1;cpu->x_flag=0;cpu->X=0;cpu->S=0x2ce;
    word(0x1f15,0x8011);word(0x1f6d,0);word(0x68,0xb213);
    address(0xb217,0xc5858a);address(0xdf,0xc00387);address(cpu->S+17,0xc36685);
    SemAccepted(cpu,0xc21c90);
}
static void transfer(CpuState *cpu) {
    cpu->m_flag=0;cpu->Y=0x230;word(0x1f6f,0x1102);SemTransfer(cpu,0xc2212e);
}
static void play(uint8_t *ram) {
    ram[8]=17;ram[0x230]=2;ram[0x231]=17;ram[0x294]=0x15;ram[0x295]=0x3d;
    PrideSemanticSpc(0x1bcb,0,0,0x2c,ram);PrideSemanticSpc(0x1be3,4,4,0x2c,ram);
    PrideSemanticSpc(0xfd1,0x3d,8,0,ram);PrideSemanticSpc(0xd34,8,7,0,ram);
    PrideSemanticLatchKon(128);PrideSemanticCommit(7);
}
static void lifecycle(CpuState *cpu,unsigned pc,uint8_t *ram) {
    uint8_t wram[131072],aram[65536];CpuState old=*cpu;
    memcpy(wram,g_ram,sizeof wram);memcpy(aram,ram,sizeof aram);
    SemDriverCpu(cpu,pc);
    CHECK(!memcmp(wram,g_ram,sizeof wram));CHECK(!memcmp(aram,ram,sizeof aram));CHECK(!memcmp(&old,cpu,sizeof old));
}
int main(int argc,char **argv) {
    CHECK(argc==2);uint8_t ram[65536];FILE *file=fopen(argv[1],"rb");CHECK(file);
    CHECK(fread(ram,1,sizeof ram,file)==sizeof ram);fclose(file);
    Apu apu={ram};Snes snes={&apu};g_snes=&snes;CpuState cpu={0};
    CHECK(SemDriverCheck(ram));
    for(unsigned at=0x600;at<0x1e00;at++) {
        ram[at]^=1;
        int operand=at==0x1a76 || at==0x1a77 || at==0x1a7f || at==0x1a80;
        CHECK(SemDriverCheck(ram)==operand);ram[at]^=1;
    }
    accept(&cpu);transfer(&cpu);play(ram);CHECK(PrideSemanticVoice(7));
    accept(&cpu);CHECK(atomic_load(&s_sem_queue[0]));
    cpu.m_flag=1;cpu.x_flag=0;cpu.DB=0;lifecycle(&cpu,0xc21e15,ram);
    CHECK(!atomic_load(&s_sem_queue[0]));CHECK(PrideSemanticVoice(7));
    accept(&cpu);transfer(&cpu);CHECK(atomic_load(&s_sem_ring[44]));
    cpu.m_flag=1;cpu.DB=0;lifecycle(&cpu,0xc21e15,ram);
    CHECK(atomic_load(&s_sem_ring[44]));play(ram);CHECK(PrideSemanticVoice(7));
    cpu.m_flag=1;cpu.x_flag=0;cpu.DB=0;lifecycle(&cpu,0xc22349,ram);CHECK(PrideSemanticVoice(7));
    ram[0x600]^=1;lifecycle(&cpu,0xc22349,ram);CHECK(!PrideSemanticVoice(7));ram[0x600]^=1;
    accept(&cpu);transfer(&cpu);play(ram);CHECK(PrideSemanticVoice(7));
    cpu.m_flag=1;cpu.x_flag=0;lifecycle(&cpu,0xc21ebf,ram);CHECK(!PrideSemanticVoice(7));
    accept(&cpu);transfer(&cpu);play(ram);CHECK(PrideSemanticVoice(7));
    cpu.m_flag=1;cpu.x_flag=1;lifecycle(&cpu,0xc21955,ram);CHECK(!PrideSemanticVoice(7));
    printf("PASS %u driver lifecycle checks\n",checks);return 0;
}
'''


def main():
    out=ROOT/'build/pride-lizard-launch-work/driver-lifecycle-component';out.mkdir()
    stub=out/'snes';stub.mkdir()
    (stub/'interp_bridge.h').write_text('''#include <stdint.h>
typedef struct { unsigned D,DB,m_flag,x_flag,X,Y,S; } CpuState;
static int interp_bridge_add_pre_opcode_hook(unsigned pc,void (*fn)(CpuState *,uint32_t)) { return 1; }
''')
    (stub/'apu.h').write_text('#pragma once\ntypedef struct { uint8_t *ram; } Apu;\n')
    (stub/'snes.h').write_text('#pragma once\n#include "apu.h"\ntypedef struct { Apu *apu; } Snes;\n')
    source=out/'component.c';source.write_text(SOURCE);exe=out/'component.exe'
    native=ROOT/'engine/snesrecomp/runner/src';sha=native/'sha256.c'
    command=['C:/mingw32/bin/gcc.exe','-std=c11','-O2','-I',str(out),'-I',str(ROOT/'tools'),'-I',str(native),str(source),str(sha),'-o',str(exe)]
    subprocess.run(command,check=True,capture_output=True)
    fixture=ROOT/'build/pride-lizard-launch-work/player/spc-voice-owner-audit/native/aram_1400.bin'
    output=subprocess.check_output([str(exe),str(fixture)],text=True);print(output,end='')
    (out/'run.log').write_text(output)
    paths=[Path(__file__),ROOT/'tools/native_bounce_semantic_owner2.h',
        ROOT/'tools/native_bounce_driver_lifecycle.h',sha,native/'sha256.h',source,fixture,*stub.glob('*.h')]
    report=dict(result='PASS',output=output,command=command,
        scope='driver code mutations, known upload, queued/ring/voice ownership and resets',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
