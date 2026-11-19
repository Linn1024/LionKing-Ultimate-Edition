#include "tlk_pickup_audio.h"
#include "tlk_audio.h"
#include "tlk_guest.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned frame;
static unsigned word(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static unsigned address_at(unsigned at) { return word(at)|(unsigned)g_ram[at+2]<<16; }
static void tick(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc55acc || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag ||
       word(0x2000) || (!TlkAudioGraveyardScene() && (word(0x1ff9e) ||
       (address_at(0xdf)!=0xc00387 && address_at(0xdf)!=0xc0080d))))return;
    unsigned actor=word(0x68);
    if(actor<0x8000 || actor>0xff80 || address_at(actor+4)!=0xc5858f ||
       address_at(actor+0x30)!=0xc55a66 || word(actor+0x2c)!=36)return;
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8 || !(g_ram[draw+9]&0x40))return;
    /* Both originals initialize this shared HUD popup to36. Only MD plays
     * FM112 here. Observe the original initializer, not an elapsed host timer;
     * ordinary resumed updates cannot replay the entry event. */
    int emitted=TlkAudioPickupArrivalTrigger();
    static FILE *trace;
    const char *path=getenv("TLK_PICKUP_ARRIVAL_TRACE");
    if(path) {
        if(!trace) { trace=fopen(path,"w");if(trace)fputs("last_audio_frame,actor,timer,emitted\n",trace); }
        if(trace) { fprintf(trace,"%u,%04x,36,%d\n",frame,actor,emitted);fflush(trace); }
    }
}
void TlkPickupAudioInstall(unsigned value) {
    frame=value;interp_bridge_add_pre_opcode_hook(0xc55acc,tick);
}
RecompReturn TlkPickupArrivalDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc55a66,3); }
