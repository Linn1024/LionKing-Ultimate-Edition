/* MD adult hyenas use the live one-based stage for their ordinary cull rule.
 * Native handlers load a cached stage. Keep the original culling branches,
 * actor updates and contact tests; select only the source stage operand. */
#include "tlk_adult_hyena.h"
#include "tlk_resources.h"
#include "tlk_audio.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static unsigned pointer(unsigned p){return word(p)|(unsigned)g_ram[p+2]<<16;}
static void before(CpuState*c,uint32_t pc){
    (void)pc;
    if(c->PB!=0xc1||c->DB!=0x7e||c->m_flag||c->x_flag||c->_flag_D||
       c->D<0x600||c->D>=0x1f00||!TlkResourcesUseMd("gameplay.enemies.hyenas.adult_culling"))return;
    unsigned level=word(0x1ff9e),actor=word(0x68);
    if((level!=8&&level!=9)||pointer(0xdf)!=0xc00517+(level-8)*50||c->A!=word(0xf93a)||
       actor<0xb293||actor>=0xdc13||((actor-0xb213)&127)||pointer(actor+4)!=0xc58ecc)return;
    c->A=(uint16_t)(level+1);c->_flag_N=0;c->_flag_Z=0;cpu_mirrors_to_p(c);
}
static const unsigned loads[]={0xc1ac58,0xc1ad80,0xc1aeae,0xc1afd6,0xc1b175,0xc1b2ec,0xc1b72a};
void (*g_tlk_adult_hyena_pc_hook)(CpuState*,uint32_t);
static void after(CpuState*c,uint32_t pc){
    if(pc==0xc1ac50 || pc==0xc1ad78){TlkAudioAdultHyenaTauntEntry(c,pc);return;}
    for(unsigned i=0;i<sizeof loads/sizeof*loads;i++)if(pc==loads[i]){before(c,pc+3);return;}
}
void TlkAdultHyenaInstall(void){
    g_tlk_adult_hyena_pc_hook=after;
    interp_bridge_add_pre_opcode_hook(0xc1ac50,TlkAudioAdultHyenaTauntEntry);
    interp_bridge_add_pre_opcode_hook(0xc1ad78,TlkAudioAdultHyenaTauntEntry);
    for(unsigned i=0;i<sizeof loads/sizeof*loads;i++)interp_bridge_add_pre_opcode_hook(loads[i]+3,before);
}
