/* Original MD entrance countdown window; no actor/timer/audio state mutation. */
#include "tlk_hyena_entrance.h"
#include "tlk_resources.h"
#include "tlk_camera.h"
#include "common_rtl.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned at){return g_ram[at]|(unsigned)g_ram[at+1]<<8;}
static unsigned pointer(unsigned at){return word(at)|(unsigned)g_ram[at+2]<<16;}
static int source_known,previous_source,previous_coconut_source;
void TlkHyenaEntrancePrepareSource(void){
    if(!source_known){previous_source=TlkResourcesUseMd("gameplay.levels.pride_lands.hyena_entrance_window");previous_coconut_source=TlkResourcesUseMd("gameplay.levels.hakuna_matata.coconut_lifetime");source_known=1;}
}
int TlkHyenaEntranceProfileChanged(void){
    int source=TlkResourcesUseMd("gameplay.levels.pride_lands.hyena_entrance_window");
    int coconut=TlkResourcesUseMd("gameplay.levels.hakuna_matata.coconut_lifetime");
    int changed=source_known && (source!=previous_source || coconut!=previous_coconut_source);
    previous_source=source;previous_coconut_source=coconut;source_known=1;return changed;
}
/* Shared native C03B76 / original MD1A7CC0 lifetime query. Only this
 * coconut call selects the wider viewport; the caller still owns deletion. */
static void coconut_window(CpuState *cpu,uint32_t pc){
    if(pc!=0xc03bdb || cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag ||
       cpu->_flag_D || cpu->_flag_C || cpu->D<0x622 || cpu->D>0x1fd0 ||
       cpu->S<0x100 || cpu->S>0x1ff0 || word(0x1ff9e)!=5 || word(0x2000) ||
       pointer(0xdf)!=0xc00481)return;
    unsigned actor=word(0x68),sp=cpu->S,camera=word(0xaa);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       pointer(0x68)!=0x7e0000+actor || pointer(actor+4)!=0xc58e84 ||
       pointer(actor+48)!=0xc053d4 || camera<0xb293 || camera>=0xdc13 ||
       ((camera-0xb213)&127) || cpu->A>3600 || cpu->A!=word(camera+8) ||
       cpu->A!=word(cpu->D+0x28) || cpu->D!=word(sp+1)+0x26 ||
       pointer(sp+4)!=0xc054b0 || word(sp+7)!=128 || word(sp+9)!=128 ||
       word(0xa68c)!=cpu->D+0x2e)return;
    unsigned before=cpu->A,selected=TlkResourcesUseMd("gameplay.levels.hakuna_matata.coconut_lifetime");
    unsigned extra=selected?64:0;
    int viewport=TlkCameraViewWidth(),canonical=TlkResourcesViewportForScene(5);
    /* The selected console limit remains independent. Optional expanded
     * activation moves the camera farther left, so retain projectiles through
     * the additional visible columns instead of deleting them at birth. */
    if(viewport>canonical)extra+=(unsigned)(viewport-canonical);
    cpu->A=(uint16_t)(cpu->A+extra);
    /* Preserve CLC and the original ADC/comparisons, vertical bounds and
     * lifetime callback. No position, velocity, timer or result forcing. */
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char*p=getenv("TLK_COCONUT_WINDOW_TRACE");if(p)trace=fopen(p,"w");if(trace)fputs("field,actor,camera_x,selected_operand,selected_width,x,y\n",trace);}
    if(trace){fprintf(trace,"%u,%04x,%u,%u,%u,%u,%u\n",snes_frame_counter+1,actor,before,cpu->A,256+extra,word(actor+8),word(actor+10));fflush(trace);}
}

void TlkHyenaEntranceWindow(CpuState *cpu,uint32_t pc){
    coconut_window(cpu,pc);
    if(pc!=0xc03bdb || cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag ||
       cpu->_flag_D || cpu->_flag_C || cpu->D<0x622 || cpu->D>0x1fd0 ||
       cpu->S<0x100 || cpu->S>0x1ff0 || word(0x1ff9e) || word(0x2000) ||
       (pointer(0xdf)!=0xc00387 && pointer(0xdf)!=0xc0080d))return;
    unsigned actor=word(0x68),sp=cpu->S;
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       pointer(0x68)!=0x7e0000+actor || pointer(actor+4)!=0xc58c68 ||
       pointer(actor+0x30)!=0xc143ae || word(0xaa)!=0xb293 ||
       cpu->A>1600 || cpu->A!=word(0xb29b) || cpu->A!=word(cpu->D+0x28) ||
       cpu->D!=word(sp+1)+0x22 || pointer(sp+4)!=0xc14480 ||
       word(sp+7)!=64 || word(sp+9)!=64 || word(0xa68c)!=cpu->D+0x2e)return;
    if(!TlkResourcesUseMd("gameplay.levels.pride_lands.hyena_entrance_window"))return;
    /* Original CLC precedes this ADC #$0100. Bias camera X by64 so that the
     * original addition produces MD's320-pixel right bound. Its subsequent
     * arithmetic, comparisons, return flags and countdown remain original. */
    unsigned before=cpu->A;cpu->A=(uint16_t)(cpu->A+64);
    static FILE *trace;const char *path=getenv("TLK_HYENA_ENTRANCE_TRACE");
    if(path){
        if(!trace){trace=fopen(path,"w");if(trace)fputs("field,actor,camera_x,selected_operand,timer\n",trace);}
        if(trace){fprintf(trace,"%u,%04x,%u,%u,%u\n",(unsigned)snes_frame_counter+1,actor,before,cpu->A,word(actor+0x2c));fflush(trace);}
    }
}
