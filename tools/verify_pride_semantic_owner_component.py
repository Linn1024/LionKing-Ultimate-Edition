"""Exercise unrelated callers, voice reuse and delayed key-on on the real prototype."""
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
#include "native_bounce_semantic_owner2.h"
static unsigned checks;
#define CHECK(v) do { assert(v);checks++; } while(0)
static void word(unsigned at,unsigned value) { g_ram[at]=value;g_ram[at+1]=value>>8; }
static void address(unsigned at,unsigned value) { word(at,value);g_ram[at+2]=value>>16; }
static void cpu_call(void (*callback)(CpuState *,uint32_t),CpuState *cpu) {
    uint8_t before[sizeof g_ram];memcpy(before,g_ram,sizeof before);CpuState old=*cpu;
    callback(cpu,0);CHECK(!memcmp(before,g_ram,sizeof before));CHECK(!memcmp(&old,cpu,sizeof old));
}
static void flow(CpuState *cpu,unsigned caller) {
    cpu->D=0x1f00;cpu->DB=0x7e;cpu->m_flag=1;cpu->x_flag=0;
    cpu->X=0;cpu->S=0x2ce;address(cpu->S+17,caller-1);
    cpu_call(SemAccepted,cpu);
    cpu->m_flag=0;cpu->Y=0x230;word(0x1f6f,0x1102);
    cpu_call(SemTransfer,cpu);
}
static void allocate(unsigned voice) {
    static uint8_t aram[65536];memset(aram,0,sizeof aram);
    memcpy(aram+0x1bcb,"\xf6\x04\x02\x1c\x5d",5);
    memcpy(aram+0x1be3,"\xeb\xeb\xf6\x05\x02",5);
    memcpy(aram+0xfd1,"\xd5\x51\x03\xd5\xa9\x03",6);
    memcpy(aram+0xd34,"\xd5\x27\x05",3);
    aram[8]=17;aram[0x230]=2;aram[0x231]=17;
    aram[0x294]=0x15;aram[0x295]=0x3d;aram[0x3d08]=17;aram[0x3d09]=1;
    uint8_t before[65536];memcpy(before,aram,sizeof before);
    PrideSemanticSpc(0x1bcb,0,0,0x2c,aram);
    PrideSemanticSpc(0x1be3,4,4,0x2c,aram);
    PrideSemanticSpc(0xfd1,0x3d,8,0,aram);
    PrideSemanticSpc(0xd34,8,voice,0,aram);
    CHECK(!memcmp(before,aram,sizeof before));
}
int main(void) {
    CpuState cpu={0};
    word(0x1f15,0x8011);word(0x68,0xb213);address(0xb217,0xc5858a);
    address(0xdf,0xc00387);
    /* Upper WRAM's second byte must not alias low bank FF9F. */
    g_ram[0xff9f]=0x7f;
    flow(&cpu,0xc36686);allocate(7);
    CHECK(!PrideSemanticVoice(7));
    PrideSemanticLatchKon(128);PrideSemanticCommit(7);CHECK(PrideSemanticVoice(7));
    /* An unrelated caller of the SAME program must keep native audio. */
    flow(&cpu,0xc2e99f);allocate(7);CHECK(PrideSemanticVoice(7));
    PrideSemanticLatchKon(128);CHECK(PrideSemanticVoice(7));
    PrideSemanticCommit(7);CHECK(!PrideSemanticVoice(7));
    /* KON captures its candidate; a later software assignment cannot retag it. */
    flow(&cpu,0xc36686);allocate(5);PrideSemanticLatchKon(32);
    flow(&cpu,0xc36369);allocate(5);PrideSemanticCommit(5);CHECK(PrideSemanticVoice(5));
    PrideSemanticLatchKon(32);PrideSemanticCommit(5);CHECK(!PrideSemanticVoice(5));
    /* A transferred packet with no accepted caller cannot inherit old identity. */
    cpu.m_flag=0;cpu.X=0;cpu.Y=0x230;cpu_call(SemTransfer,&cpu);allocate(7);
    PrideSemanticLatchKon(128);PrideSemanticCommit(7);CHECK(!PrideSemanticVoice(7));
    flow(&cpu,0xc36686);allocate(1);PrideSemanticLatchKon(2);PrideSemanticCommit(1);
    CHECK(PrideSemanticVoice(1));PrideSemanticReset();
    for(unsigned voice=0;voice<8;voice++)CHECK(!PrideSemanticVoice(voice));
    printf("PASS %u semantic ownership checks\n",checks);return 0;
}
'''


def main():
    out=ROOT/'build/pride-lizard-launch-work/semantic-owner-component';out.mkdir()
    stub=out/'snes';stub.mkdir()
    (stub/'interp_bridge.h').write_text('''#include <stdint.h>
typedef struct { unsigned D,DB,m_flag,x_flag,X,Y,S; } CpuState;
static int interp_bridge_add_pre_opcode_hook(unsigned pc,void (*fn)(CpuState *,uint32_t)) { return 1; }
''')
    source=out/'component.c';source.write_text(SOURCE)
    exe=out/'component.exe'
    command=['C:/mingw32/bin/gcc.exe','-std=c11','-O2','-I',str(out),'-I',str(ROOT/'tools'),str(source),'-o',str(exe)]
    subprocess.run(command,check=True,capture_output=True)
    result=subprocess.check_output([str(exe)],text=True);print(result,end='')
    (out/'run.log').write_text(result)
    paths=[Path(__file__),ROOT/'tools/native_bounce_semantic_owner2.h',source,stub/'interp_bridge.h']
    report=dict(result='PASS',output=result,command=command,
        scope='synthetic ownership lifecycle, not full game/save/thread coverage',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
