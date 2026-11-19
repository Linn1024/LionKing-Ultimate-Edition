/* The original MD count-up starts at1 and finishes at60:59 subsequent updates.
 * Supply that wait to the ordinary native room-completion countdown. */
#include "tlk_return_exit.h"
#include "tlk_late_scene_data.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static unsigned pointer(unsigned p){return word(p)|(unsigned)g_ram[p+2]<<16;}
static void before(CpuState*c,uint32_t pc){
    (void)pc;const uint16_t*r=TlkLateSceneReturnExitRules();
    if(!r||word(0x1ff9e)!=8||pointer(0xdf)!=0xc00517||c->PB!=0xc0||c->DB!=0x7e||c->D||
       c->m_flag||!c->x_flag||c->_flag_D||c->Y!=0x2e||c->A!=r[0]||word(0xa6c4)!=4||
       !TlkResourcesUseMd("gameplay.levels.simbas_return.exit_timing"))return;
    c->A=(uint16_t)(r[2]-r[1]);c->_flag_N=!!(c->A&32768);c->_flag_Z=!c->A;cpu_mirrors_to_p(c);
}
void (*g_tlk_return_exit_pc_hook)(CpuState*,uint32_t);
static void after(CpuState*c,uint32_t pc){if(pc==0xc0d439)before(c,0xc0d43c);}
void TlkReturnExitInstall(void){g_tlk_return_exit_pc_hook=after;interp_bridge_add_pre_opcode_hook(0xc0d43c,before);}
