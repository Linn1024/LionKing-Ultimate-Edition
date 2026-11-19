#include "tlk_lizard_audio.h"
#include "tlk_audio.h"
#include "tlk_guest.h"
#include "tlk_defeat_audio_scene.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned frame;
static unsigned word(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static unsigned address_at(unsigned at) { return word(at)|(unsigned)g_ram[at+2]<<16; }
static int scene(void) {
    return (!word(0x1ff9e) && (address_at(0xdf)==0xc00387 || address_at(0xdf)==0xc0080d)) ||
        (word(0x1ff9e)==4 && address_at(0xdf)==0xc0044f);
}
void TlkLizardAttackVoice(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc1650e || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       !scene() || word(0x2000))return;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       address_at(actor+4)!=0xc58ca4 || address_at(actor+0x30)!=0xc16451 ||
       word(actor+0x2c)!=32 || !word(actor+0x44) ||
       cpu->D<0x600 || cpu->D>0x1fdb || word(0xa68c)!=cpu->D+0x24)return;
    /* This seam follows the original early contact/visibility guards. Original
     * action counter32 owns the cue and advances normally; no actor writes or
     * host event latch are added. Launch/defeat actions remain separate. */
    int emitted=TlkAudioLizardAttackTrigger();
    static FILE *trace;const char *path=getenv("TLK_LIZARD_ATTACK_TRACE");
    if(path) {
        if(!trace){trace=fopen(path,"w");if(trace)fputs("field,actor,counter,emitted\n",trace);}
        if(trace){fprintf(trace,"%u,%04x,32,%d\n",(unsigned)snes_frame_counter+1,actor,emitted);fflush(trace);}
    }
}
static void launch_tick(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc153f2 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag ||
       !scene() || word(0x2000))return;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       address_at(actor+4)!=0xc58c50 || address_at(actor+0x30)!=0xc15363 ||
       word(actor+0x2c)!=20)return;
    /* MD199CC2 emits FM123 after timer20 is installed. Native C15363 is
     * silent. Ongoing updates skip this initialization seam; guest state
     * owns the event, without a host latch or guest writes. */
    int emitted=TlkAudioLizardLaunchTrigger();
    static FILE *trace;const char *path=getenv("TLK_LIZARD_LAUNCH_TRACE");
    if(path) {
        if(!trace) { trace=fopen(path,"w");if(trace)fputs("last_audio_frame,actor,timer,emitted\n",trace); }
        if(trace) { fprintf(trace,"%u,%04x,20,%d\n",frame,actor,emitted);fflush(trace); }
    }
}
static void tick(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc16677 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || !TlkDefeatAudioScene(g_ram))return;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       word(actor+0x30)!=0x6608 || word(actor+0x32)!=0xc1 || word(actor+0x2c)!=30 ||
       cpu->D<0x600 || cpu->D>0x1fdb || word(cpu->D)!=actor || word(0xa68c)!=cpu->D+0x22)return;
    /* MD 19C554 and native C16608 both initialize32 and decrement on each
     * update. Only MD emits FM165 before decrementing30. The original native
     * timer owns the event, including continued/saved actions; no guest writes. */
    int emitted=TlkAudioLizardDefeatTrigger();
    static FILE *trace;const char *path=getenv("TLK_LIZARD_DEFEAT_TRACE");
    if(path) {
        if(!trace) { trace=fopen(path,"w");if(trace)fprintf(trace,"last_audio_frame,actor,timer,emitted,field,scene,descriptor\n"); }
        if(trace) { fprintf(trace,"%u,%04x,30,%d,%u,%06x,%06x\n",frame,actor,emitted,(unsigned)snes_frame_counter+1,address_at(0xdf),address_at(actor+4));fflush(trace); }
    }
}
void TlkLizardAudioInstall(unsigned value) {
    frame=value;interp_bridge_add_pre_opcode_hook(0xc16677,tick);
    interp_bridge_add_pre_opcode_hook(0xc153f2,launch_tick);
}
RecompReturn TlkLizardDefeatDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc16608,3); }

RecompReturn TlkLizardLaunchDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc15363,3); }
