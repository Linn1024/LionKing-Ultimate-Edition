#include "tlk_scar_contact.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
/* Both source routines already use a40-unit overlap range. MD additionally
 * moves Simba to its edge after the ordinary contact/direction/input-mask
 * branches. Keep that behavior separate from either actor's selected bounds. */
enum { CONTACT_RANGE=40 };
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
static unsigned pointer(unsigned p){return word(p)|(unsigned)g_ram[p+2]<<16;}
static void put(unsigned p,unsigned v){g_ram[p]=(uint8_t)v;g_ram[p+1]=(uint8_t)(v>>8);}
void (*g_tlk_scar_contact_pc_hook)(CpuState*,uint32_t);
static void separate(CpuState*c,uint32_t pc){
    if((pc!=0xc66ae0&&pc!=0xc66b1f)||word(0x1ff9e)!=9||pointer(0xdf)!=0xc00549||
       c->PB!=0xc6||c->DB!=0x7e||c->m_flag||c->x_flag||c->_flag_D||c->D<0x600||c->D>=0x1f00||
       word(0x6e)!=0xb213||!TlkResourcesUseMd("gameplay.levels.pride_rock.scar_contact_response"))return;
    unsigned a=word(0x68),desc=pointer(a+4);
    if(a<0xb293||a>=0xdc13||((a-0xb213)&127)||
       (desc!=0xc585e8&&desc!=0xc585f4&&desc!=0xc58600))return;
    int delta=(int16_t)(word(0xb21b)-word(a+8));
    if(pc==0xc66ae0&&delta<0&&delta>=-CONTACT_RANGE)put(0xb21b,word(a+8)-CONTACT_RANGE);
    if(pc==0xc66b1f&&delta>0&&delta<=CONTACT_RANGE)put(0xb21b,word(a+8)+CONTACT_RANGE);
}
void TlkScarContactInstall(void){
    /* AOT's post-PLA seam and the interpreter's pre-PLA seam both follow the
     * successful input-mask call. This rule reads no CPU result/stack/flags. */
    g_tlk_scar_contact_pc_hook=separate;
    interp_bridge_add_pre_opcode_hook(0xc66ae0,separate);
    interp_bridge_add_pre_opcode_hook(0xc66b1f,separate);
}
