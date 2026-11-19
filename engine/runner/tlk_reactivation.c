#include "tlk_reactivation.h"
#include "tlk_reactivation_data.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
void (*g_tlk_reactivation_pc_hook)(CpuState *,uint32_t);
static unsigned word(unsigned a) { return g_ram[a]|(unsigned)g_ram[a+1]<<8; }
static void pre(CpuState *cpu,uint32_t pc) {
    unsigned native,external,actor=word(0x68);
    if(!TlkResourcesUseMd("gameplay.levels.pride_lands.lizard_reactivation") ||
       word(0x1ff9e) || (word(0xdf)!=0x387 && word(0xdf)!=0x80d) || g_ram[0xe1]!=0xc0 ||
       cpu->D || cpu->DB!=0x7e || !cpu->m_flag || !cpu->x_flag || cpu->Y!=5 ||
       word(0x8e)!=0x8ca4 || g_ram[0x90]!=0xc5 || actor<0xb313 || actor>0xc193 ||
       ((actor-0xb213)&127) || word(actor+0x44)!=14 ||
       !TlkReactivationDataFlags(&native,&external) || (cpu->A&255)!=native)return;
    cpu->A=(cpu->A&0xff00)|external;cpu->_flag_N=!!(external&128);cpu->_flag_Z=!external;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened) { const char *p=getenv("TLK_LIZARD_REACTIVATION_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fprintf(trace,"pc,actor,marker,native,selected\n"); }
    if(trace) { fprintf(trace,"%06x,%04x,14,%u,%u\n",pc,actor,native,external);fflush(trace); }
}
static void after(CpuState *cpu,uint32_t pc) { pre(cpu,pc+2); }
void TlkReactivationInstall(void) {
    g_tlk_reactivation_pc_hook=after;
    interp_bridge_add_pre_opcode_hook(0xc0cc38,pre);interp_bridge_add_pre_opcode_hook(0x00cc38,pre);
}
