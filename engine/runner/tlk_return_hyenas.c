/* Installation-owned doorway lists feed the ordinary native hyena spawn loop. */
#include "tlk_return_hyenas.h"
#include "tlk_late_scene_data.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static unsigned pointer(unsigned p){return word(p)|(unsigned)g_ram[p+2]<<16;}
static void load(CpuState*c,unsigned value){c->A=(uint16_t)value;c->_flag_N=!!(value&32768);c->_flag_Z=!value;cpu_mirrors_to_p(c);}
static void before(CpuState*c,uint32_t pc){
    if(word(0x1ff9e)!=8||pointer(0xdf)!=0xc00517||c->PB!=0xc0||c->DB!=0x7e||
       c->D||c->m_flag||c->x_flag||c->_flag_D||pointer(0xb243)!=0xc3887a||word(0xb241)!=2||
       !TlkResourcesUseMd("gameplay.levels.simbas_return.doorway_hyenas"))return;
    unsigned encoded=g_ram[0xb253],ptr,nc,mc;if(encoded<32||!TlkLateSceneReturnHyenas(encoded-32,&ptr,&nc,&mc))return;
    if(pc==0xc076df){if(c->X==ptr&&c->A==nc)load(c,mc);return;}
    if(c->X<ptr+2||((c->X-ptr-2)&3))return;
    unsigned slot=(c->X-ptr-2)/4,md;
    if(slot<mc&&TlkLateSceneReturnHyenaPosition(encoded-32,slot,pc==0xc076ed,c->A,&md))load(c,md);
}
void (*g_tlk_return_hyenas_pc_hook)(CpuState*,uint32_t);
static const struct{unsigned after,before;}sites[]={
    {0xc076db,0xc076df},{0xc076e9,0xc076ed},{0xc076ee,0xc076f2}};
static void after(CpuState*c,uint32_t pc){
    for(unsigned i=0;i<sizeof sites/sizeof*sites;i++)if(pc==sites[i].after){before(c,sites[i].before);return;}
}
void TlkReturnHyenasInstall(void){
    g_tlk_return_hyenas_pc_hook=after;
    for(unsigned i=0;i<sizeof sites/sizeof*sites;i++)interp_bridge_add_pre_opcode_hook(sites[i].before,before);
}
