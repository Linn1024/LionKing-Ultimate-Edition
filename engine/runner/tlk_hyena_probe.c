/* Independent original MD walking-query height; actor position stays original. */
#include "tlk_hyena_probe.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static unsigned pointer(unsigned at) { return word(at)|(unsigned)g_ram[at+2]<<16; }
static int source_known,previous_source;
void TlkHyenaProbePrepareSource(void) {
    if(!source_known) {
        previous_source=TlkResourcesUseMd("gameplay.levels.pride_lands.hyena_probe_height");
        source_known=1;
    }
}
int TlkHyenaProbeProfileChanged(void) {
    int selected=TlkResourcesUseMd("gameplay.levels.pride_lands.hyena_probe_height");
    int changed=source_known && selected!=previous_source;
    previous_source=selected;source_known=1;return changed;
}
void TlkHyenaWalkingProbe(CpuState *cpu,uint32_t pc) {
    if((pc!=0xc0c5fe && pc!=0xc0c6e3 && pc!=0x00c5fe && pc!=0x00c6e3) ||
       (cpu->PB!=0xc0 && cpu->PB!=0) || cpu->PB!=(pc>>16) || cpu->DB!=0x7e ||
       cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
       word(0x1ff9e) || word(0x2000) ||
       (pointer(0xdf)!=0xc00387 && pointer(0xdf)!=0xc0080d))return;
    unsigned actor=word(0x68),sp=cpu->S;
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       pointer(0x68)!=0x7e0000+actor || pointer(actor+4)!=0xc58c68 ||
       pointer(actor+0x30)!=0xc13c83 || cpu->A!=word(actor+10) ||
       sp<0x100 || sp>0x1fe6)return;
    unsigned outer=word(sp+3),left=(pc&65535)==0xc6e3;
    if(word(sp+1)!=(left?0xc816:0xc840) ||
       pointer(sp+6)!=(left?0xc14070:0xc1408b) ||
       word(sp+9)!=(left?0xffe0:0x20) || outer<0x600 || outer>0x1fc5 ||
       word(0xa68c)!=outer+0x3a)return;
    if(!TlkResourcesUseMd("gameplay.levels.pride_lands.hyena_probe_height"))return;
    /* C0C5FE/C0C6E3 next store A as query Y. MD wrappers subtract8 before
     * the shared lookup's own subtract8. Preserve original CPU flags and all
     * actor/queue state; the subsequent original instructions own the query. */
    unsigned native_y=cpu->A;cpu->A=(uint16_t)(cpu->A-8);
    static FILE *trace;const char *path=getenv("TLK_HYENA_PROBE_TRACE");
    if(path) {
        if(!trace){trace=fopen(path,"w");if(trace)fputs("field,pc,actor,native_query_y,selected_query_y\n",trace);}
        if(trace){fprintf(trace,"%u,%06x,%04x,%u,%u\n",(unsigned)snes_frame_counter+1,pc,actor,native_y,cpu->A);fflush(trace);}
    }
}
