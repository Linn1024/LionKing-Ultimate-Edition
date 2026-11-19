/* Prepared MD initialization chooses a native controller through the normal
 * constructor dispatcher. Reveal retains the ordinary comparison branch. */
#include "tlk_scar_activation.h"
#include "tlk_late_scene_data.h"
#include "tlk_resources.h"
#include "tlk_wide.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static unsigned pointer(unsigned p){return word(p)|(unsigned)g_ram[p+2]<<16;}
static void trace(unsigned pc,unsigned actor,unsigned before,unsigned after){
    static FILE*f;static int opened;if(!opened){opened=1;const char*p=getenv("TLK_SCAR_ACTIVATION_TRACE");if(p)f=fopen(p,"w");if(f)fputs("field,pc,actor,before,after\n",f);}
    if(f){fprintf(f,"%u,%06x,%04x,%u,%u\n",snes_frame_counter+1,pc,actor,before,after);fflush(f);}
}
static void before(CpuState*c,uint32_t pc){
    /* C672A8 is Scar's own escape-retirement query. Its original caller
     * still decides when to remove him; enlarge only the camera operands.
     * This viewport correction is independent of the SNES/Genesis AI choice. */
    if(pc==0xc672f2 || pc==0xc6731b || pc==0xc67348){
        if(word(0x1ff9e)!=9 || pointer(0xdf)!=0xc00549 || c->PB!=0xc6 ||
           c->DB!=0x7e || c->m_flag || c->x_flag || c->_flag_D ||
           c->D<0x600 || c->D>0x1f00)return;
        unsigned actor=word(0x68),descriptor=pointer(actor+4);
        if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
           (descriptor!=0xc585e8 && descriptor!=0xc585f4 && descriptor!=0xc58600))return;
        int left,right,bottom;if(!TlkWideRetreatMargins(&left,&right,&bottom))return;
        unsigned old=c->A;
        if(pc==0xc672f2){
            unsigned bound=(unsigned)(-40-left)&65535,result=(c->A-bound)&65535;
            c->_flag_C=c->A>=bound;c->_flag_N=!!(result&32768);c->_flag_Z=!result;
        }else{
            if(pc==0xc6731b && c->A!=296)return;
            c->A=(uint16_t)(c->A+(pc==0xc6731b?right:bottom));
            c->_flag_N=!!(c->A&32768);c->_flag_Z=!c->A;
        }
        cpu_mirrors_to_p(c);trace(pc,actor,old,c->A);return;
    }
    if(word(0x1ff9e)!=9||pointer(0xdf)!=0xc00549||word(0x2000)!=65535||c->DB!=0x7e||c->m_flag||c->_flag_D||
       !TlkResourcesUseMd("gameplay.levels.pride_rock.scar_activation"))return;
    unsigned actor=word(0x68);if(actor<0xb293||actor>=0xdc13||((actor-0xb213)&127))return;
    unsigned descriptor=pointer(actor+4);
    if(pc==0xc0cc55||pc==0xc0cc5b){
        unsigned second=pc==0xc0cc5b,native,md;
        if(c->PB!=0xc0||c->D||!c->x_flag||c->Y!=9+second||pointer(actor+48)||
           !TlkLateSceneScarActivation(descriptor,&native,&md)||c->A!=(second?native>>8:native&65535))return;
        unsigned old=c->A;c->A=(uint16_t)(second?md>>8:md&65535);c->_flag_N=!!(c->A&32768);c->_flag_Z=!c->A;cpu_mirrors_to_p(c);trace(pc,actor,old,c->A);return;
    }
    if(pc==0xc65d76&&c->PB==0xc6&&!c->x_flag&&c->D>=0x600&&c->D<0x1f00&&
       (descriptor==0xc585e8||descriptor==0xc585f4||descriptor==0xc58600)){
        const uint16_t*r=TlkLateSceneScarRevealRules();if(!r)return;
        unsigned input=c->A,result=(input-r[1])&65535;
        /* CMP changes N/Z/C while preserving A and V. */
        c->_flag_C=input>=r[1];c->_flag_N=!!(result&32768);c->_flag_Z=!result;cpu_mirrors_to_p(c);trace(pc,actor,input,result);
    }
}
void (*g_tlk_scar_activation_pc_hook)(CpuState*,uint32_t);
static const struct{unsigned after,before;}sites[]={
    {0xc0cc53,0xc0cc55},{0xc0cc59,0xc0cc5b},{0xc65d73,0xc65d76},
    {0xc672ef,0xc672f2},{0xc67318,0xc6731b},{0xc67345,0xc67348}};
static void after(CpuState*c,uint32_t pc){for(unsigned i=0;i<sizeof sites/sizeof*sites;i++)if(pc==sites[i].after){before(c,sites[i].before);return;}}
void TlkScarActivationInstall(void){g_tlk_scar_activation_pc_hook=after;for(unsigned i=0;i<sizeof sites/sizeof*sites;i++)interp_bridge_add_pre_opcode_hook(sites[i].before,before);}
