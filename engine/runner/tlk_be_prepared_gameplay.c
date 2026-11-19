/* Prepared lava operands and ordinary geyser constructor callbacks. */
#include "tlk_be_prepared_gameplay.h"
#include "tlk_be_prepared_data.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static unsigned pointer(unsigned p){return word(p)|(unsigned)g_ram[p+2]<<16;}
static void load(CpuState*c,unsigned v,uint32_t pc){
    unsigned old=c->A;c->A=(uint16_t)v;c->_flag_N=!!(c->A&32768);c->_flag_Z=!c->A;cpu_mirrors_to_p(c);
    static FILE*f;static int checked;if(!checked){checked=1;const char*p=getenv("TLK_BE_PREPARED_GAMEPLAY_TRACE");if(p)f=fopen(p,"w");if(f)fputs("field,pc,before,after\n",f);}
    if(f){fprintf(f,"%u,%06x,%u,%u\n",snes_frame_counter+1,pc,old,c->A);fflush(f);}
}
static void before(CpuState*c,uint32_t pc){
    if(word(0x1ff9e)!=7||pointer(0xdf)!=0xc004e5||c->DB!=0x7e||c->m_flag||c->_flag_D||!TlkBePreparedDataReady())return;
    if(pc==0xc0b7df||pc==0xc08560){
        unsigned retry=pc==0xc08560;
        if(c->PB!=0xc0||c->D||(!retry&&c->x_flag)||word(0xd0)!=610||word(0xd4)!=45||
           !TlkResourcesUseMd("gameplay.levels.be_prepared.emitter_positions"))return;
        unsigned base=pointer(0xe9),at=pointer(0xdc)-2;
        if(base<0x7e0000||base>0x800000-27450||at<base||at-base>=27450||((at-base)&1))return;
        unsigned cell=(at-base)/2,x=word(retry?0xa9f:0x14),y=word(retry?0xa97:0x16),md;
        if(x!=(cell%305)*16||y!=(cell/305)*16)return;
        if(TlkBePreparedEmitterMarker(cell,word(at-0x7e0000),c->A&255,&md))load(c,(c->A&0xff00)|md,pc);return;
    }
    unsigned actor=word(0x68);if(actor<0xb293||actor>=0xdc13||((actor-0xb213)&127))return;
    if(pc==0xc0cc55||pc==0xc0cc5b){
        unsigned second=pc==0xc0cc5b,native,md;
        if(c->PB!=0xc0||c->D||!c->x_flag||c->Y!=9+second||pointer(actor+4)!=0xc5874a||pointer(actor+48)||
           !TlkResourcesUseMd("gameplay.levels.be_prepared.geyser_initialization")||
           !TlkBePreparedGeyserInitialization(&native,&md)||c->A!=(second?native>>8:native&65535))return;
        load(c,second?md>>8:md&65535,pc);return;
    }
    if(c->PB!=0xc4||c->x_flag||c->D<0x600||c->D>=0x1f00||pointer(actor+4)!=0xc5878c||pointer(actor+48)!=0xc400e4||
       !TlkResourcesUseMd("gameplay.levels.be_prepared.lava_spread"))return;
    const uint16_t*r=TlkBePreparedSpreadRules();if(!r)return;
    if(pc==0xc40163&&c->A==(word(0xa68e)&r[0]))load(c,word(0xa68e)&r[1],pc);
    if(pc==0xc40168&&c->A==r[2])load(c,r[3],pc);
}
void (*g_tlk_be_prepared_pc_hook)(CpuState*,uint32_t);
static const struct{unsigned after,before;}sites[]={
    {0xc0b7dd,0xc0b7df},{0xc0855e,0xc08560},{0xc0cc53,0xc0cc55},
    {0xc0cc59,0xc0cc5b},{0xc40160,0xc40163},{0xc40165,0xc40168}};
static void after(CpuState*c,uint32_t pc){for(unsigned i=0;i<sizeof sites/sizeof*sites;i++)if(pc==sites[i].after){before(c,sites[i].before);return;}}
void TlkBePreparedGameplayInstall(void){g_tlk_be_prepared_pc_hook=after;for(unsigned i=0;i<sizeof sites/sizeof*sites;i++)interp_bridge_add_pre_opcode_hook(sites[i].before,before);}
