#include "tlk_hyena_audio.h"
#include "tlk_audio.h"
#include "tlk_guest.h"
#include "tlk_graveyard_hyena_owner.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned frame;
static unsigned word(unsigned a) { return g_ram[a]|(unsigned)g_ram[a+1]<<8; }
static unsigned pointer(unsigned a) { return word(a)|(unsigned)g_ram[a+2]<<16; }
static int scene(void) {
    return TlkAudioGraveyardScene() || (!word(0x1ff9e) &&
        (pointer(0xdf)==0xc00387 || pointer(0xdf)==0xc0080d));
}
static int graveyard_owner(unsigned actor) {
    if(!TlkAudioGraveyardScene())return 1;
    if(actor<0x8000 || actor>0xff80 || !TlkGraveyardHyenaDescriptor(pointer(actor+4)))return 0;
    unsigned draw=word(actor+12);
    return draw>=0x8000 && draw<=0xffe8 && word(draw+4)==actor+8 && !(g_ram[draw+9]&0x40);
}
void TlkHyenaVoiceEntry(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc14535 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       !scene() || word(0x2000))return;
    unsigned actor=word(0x68),old=pointer(actor+0x30);
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       (TlkAudioGraveyardScene()?!TlkGraveyardHyenaDescriptor(pointer(actor+4)):pointer(actor+4)!=0xc58c68) || !graveyard_owner(actor) || old==0xc14501 ||
       cpu->D<0x600 || cpu->D>0x1fdb || word(0xa68c)!=cpu->D+0x24)return;
    /* C14535 belongs only to the original initialization branch. The next
     * original stores install C14501; ongoing updates and restored initialized
     * actors skip this branch. No guest write or host episode latch is needed. */
    int emitted=TlkAudioHyenaVoiceTrigger();
    static FILE *trace;const char *path=getenv("TLK_HYENA_VOICE_TRACE");
    if(path) {
        if(!trace){trace=fopen(path,"w");if(trace)fputs("field,actor,from_state,emitted\n",trace);}
        if(trace){fprintf(trace,"%u,%04x,%06x,%d\n",(unsigned)snes_frame_counter+1,actor,old,emitted);fflush(trace);}
    }
}
static void enter(CpuState *cpu,uint32_t pc) {
    if (pc!=0xc141fa || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag ||
        !scene()) return;
    unsigned actor=word(0x68);
    if (actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) || !graveyard_owner(actor)) return;
    unsigned old=word(actor+0x30)|(unsigned)g_ram[actor+0x32]<<16;
    if (old==0xc141c6) return;
    /* The original first-entry branch owns this event. Its serialized actor
     * state prevents repeats on later updates or a resumed initialized actor. */
    int emitted=TlkAudioHyenaTauntTrigger();
    static FILE *trace;
    const char *path=getenv("TLK_HYENA_TAUNT_TRACE");
    if (path) {
        if (!trace) { trace=fopen(path,"w");if(trace)fprintf(trace,"frame,actor,from_state,to_state,emitted\n"); }
        if (trace) { fprintf(trace,"%u,%04x,%06x,c141c6,%d\n",frame,actor,old,emitted);fflush(trace); }
    }
}
void TlkHyenaAudioInstall(unsigned value) {
    frame=value;interp_bridge_add_pre_opcode_hook(0xc141fa,enter);
}
RecompReturn TlkHyenaTauntDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc141c6,3); }
