/* Select the installed MD doorway-entry wait; ordinary fade/teleport/input stay in charge. */
#include "tlk_return_door.h"
#include "tlk_late_scene_data.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static unsigned pointer(unsigned p){return word(p)|(unsigned)g_ram[p+2]<<16;}
static void before(CpuState*c,uint32_t pc){
    (void)pc;const uint16_t*r=TlkLateSceneReturnDoorRules();
    if(!r||word(0x1ff9e)!=8||pointer(0xdf)!=0xc00517||c->PB!=0xc3||c->DB!=0x7e||
       c->m_flag||c->x_flag||c->_flag_D||c->D<0x600||c->D>=0x1f00||word(0x68)!=0xb213||
       pointer(0xb243)!=0xc3887a||word(0xb241)||c->A!=r[0]||
       !TlkResourcesUseMd("gameplay.levels.simbas_return.doorway_timing"))return;
    c->A=r[1];c->_flag_N=!!(c->A&32768);c->_flag_Z=!c->A;cpu_mirrors_to_p(c);
}
void (*g_tlk_return_door_pc_hook)(CpuState*,uint32_t);
static void after(CpuState*c,uint32_t pc){if(pc==0xc388d8)before(c,0xc388db);}
void TlkReturnDoorInstall(void){g_tlk_return_door_pc_hook=after;interp_bridge_add_pre_opcode_hook(0xc388db,before);}
