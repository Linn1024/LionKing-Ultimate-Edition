#include "tlk_adult_ledge.h"
#include "tlk_late_scene_data.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static unsigned pointer(unsigned p){return word(p)|(unsigned)g_ram[p+2]<<16;}
static void put(unsigned p,unsigned v){g_ram[p]=(uint8_t)v;g_ram[p+1]=(uint8_t)(v>>8);}
static void load(CpuState*c,unsigned v){c->A=(uint16_t)v;c->_flag_N=!!(v&32768);c->_flag_Z=!(v&65535);cpu_mirrors_to_p(c);}
static int scope(CpuState*c){
    unsigned level=word(0x1ff9e);
    return level>=6&&level<=9&&pointer(0xdf)==0xc004b3+(level-6)*50&&word(0x2000)==65535&&
        pointer(0xb217)==0xc5858a&&c->DB==0x7e&&!c->m_flag&&!c->x_flag&&!c->_flag_D&&
        c->D>=0x600&&c->D<0x1f00&&TlkResourcesUseMd("gameplay.simba.adult_ledge_reactions");
}
static void before(CpuState*c,uint32_t pc){
    const uint16_t*r=TlkLateSceneAdultLedgeRules();if(!r||!scope(c))return;
    unsigned active=r[0],release=r[1];
    if(pc==0xc38aa2){if(word(0x6e)==0xb213)put(0xb25f,word(0xb25f)|release);return;}
    if(pc==0xc1c050||pc==0xc1c0d1){
        unsigned a=word(0x68);
        if(a>=0xb293&&a<0xdc13&&!((a-0xb213)&127)&&pointer(a+4)==0xc58ecc&&(word(0xb25f)&active)){
            /* Source active-hang predicate joins the existing mask predicate.
             * The ordinary BNE then selects the second contact/distance query
             * in both compiled and interpreted execution. */
            c->_flag_Z=0;cpu_mirrors_to_p(c);
        }
        return;
    }
    if(word(0x68)!=0xb213)return;
    if(pc==0xc33e2d||pc==0xc33e80||pc==0xc33f03||pc==0xc34017||pc==0xc3406a||pc==0xc340c6){
        /* A climb callback may already have changed action before this exit.
         * Reaching the actual exit boundary, not the new action, owns cleanup. */
        put(0xb25f,word(0xb25f)&~active);return;
    }
    unsigned action=pointer(0xb243);if(action!=0xc33d1f&&action!=0xc33f11)return;
    if(pc==0xc33dd2||pc==0xc33fbc){
        if(c->Y==0x4c&&c->A==(word(0xb25f)&~release))load(c,c->A|active);
        return;
    }
    if(pc==0xc3400a&&action==0xc33f11&&c->Y==8){
        unsigned input=(c->A-r[2])&65535,result=(input+r[3])&65535,amount=(0-r[3])&65535;
        c->_flag_C=input>=amount;c->_flag_V=!!(((input^amount)&(input^result))&32768);load(c,result);
    }
}
void (*g_tlk_adult_ledge_pc_hook)(CpuState*,uint32_t);
static const struct {unsigned after,before;} sites[]={
    {0xc38a9f,0xc38aa2},{0xc1c04e,0xc1c050},{0xc1c0cf,0xc1c0d1},
    {0xc33dcf,0xc33dd2},{0xc33fb9,0xc33fbc},{0xc34007,0xc3400a},
    {0xc33e2b,0xc33e2d},{0xc33e7e,0xc33e80},{0xc33f01,0xc33f03},
    {0xc34015,0xc34017},{0xc34068,0xc3406a},{0xc340c6,0xc340c6}};
static void after(CpuState*c,uint32_t pc){
    for(unsigned i=0;i<sizeof sites/sizeof*sites;i++)if(pc==sites[i].after){before(c,sites[i].before);return;}
}
void TlkAdultLedgeInstall(void){
    g_tlk_adult_ledge_pc_hook=after;
    for(unsigned i=0;i<sizeof sites/sizeof*sites;i++)interp_bridge_add_pre_opcode_hook(sites[i].before,before);
}
