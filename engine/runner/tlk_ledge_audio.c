#include "tlk_ledge_audio.h"
#include "tlk_audio.h"
#include "tlk_guest.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned frame;
static unsigned word(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static unsigned address_at(unsigned at) { return word(at)|(unsigned)g_ram[at+2]<<16; }
static int contact_world(void) {
    unsigned level=word(0x1ff9e),scene=address_at(0xdf);
    return level<=9 && level!=3 && word(0x2000)==(level<6?0:0xffff) &&
        (scene==0xc00387+level*50 || (!level && scene==0xc0080d) ||
         (level==9 && scene==0xc007db));
}
static void tick(CpuState *cpu,uint32_t pc) {
    if((pc!=0xc351a8 && pc!=0xc3537a) || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag ||
       cpu->S>0xfff5 || word(0x68)!=0xb213 || word(0x6e)!=0xb213 ||
       address_at(0xb217)!=0xc5858a || !contact_world())return;
    unsigned tag=word(cpu->S+4);
    /* MD195FA6/1961D6 emit FM94 before branching. Native C351A8/C3537A
     * have no entry cue. Observe the actual contact call, preserving the
     * original constructors, animation/timing and serialized guest stack. */
    int emitted=TlkAudioLedgeGrabTrigger();
    static FILE *trace;const char *path=getenv("TLK_LEDGE_GRAB_TRACE");
    if(path) {
        if(!trace) { trace=fopen(path,"w");if(trace)fputs("last_audio_frame,entry,actor,tag,emitted\n",trace); }
        if(trace) { fprintf(trace,"%u,%06x,b213,%04x,%d\n",frame,pc,tag,emitted);fflush(trace); }
    }
}
void TlkLedgeAudioInstall(unsigned value) {
    frame=value;
    interp_bridge_add_pre_opcode_hook(0xc351a8,tick);
    interp_bridge_add_pre_opcode_hook(0xc3537a,tick);
}
RecompReturn TlkLedgeLeftDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc351a8,3); }
RecompReturn TlkLedgeRightDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc3537a,3); }
