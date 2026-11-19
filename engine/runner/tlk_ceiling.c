#include "tlk_ceiling.h"
#include "tlk_resources.h"
#include "tlk_hitbox_data.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "cpu_state.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned p) { return g_ram[p]|(unsigned)g_ram[p+1]<<8; }
static unsigned pointer(unsigned p) { return word(p)|(unsigned)g_ram[p+2]<<16; }
static void trace(CpuState *cpu,uint32_t pc,const char *kind,unsigned pose,unsigned native,unsigned selected) {
    static FILE *file;static int initialized;
    if(!initialized) { const char *p=getenv("TLK_CEILING_TRACE");initialized=1;if(p)file=fopen(p,"w");
        if(file)fprintf(file,"frame,pc,kind,actor,pose,x_argument,actor_y,native,selected\n"); }
    unsigned actor=word(0x68);
    if(file) { fprintf(file,"%d,%06x,%s,%04x,%06x,%u,%u,%04x,%04x\n",snes_frame_counter,pc,kind,actor,pose,word(0x4e),word(actor+10),native,selected);fflush(file); }
    (void)cpu;
}
static void pre(CpuState *cpu,uint32_t pc) {
    int graveyard=word(0x1ff9e)==2 && pointer(0xdf)==0xc003eb;
    int pride=!word(0x1ff9e) && (pointer(0xdf)==0xc00387 || pointer(0xdf)==0xc0080d);
    int exile=word(0x1ff9e)==4 && pointer(0xdf)==0xc0044f;
    unsigned level=word(0x1ff9e);
    int adult=level>=6 && level<=9 && pointer(0xdf)==0xc004b3+(level-6)*50 && word(0x2000)==65535;
    int hakuna=word(0x1ff9e)==5 && pointer(0xdf)==0xc00481 && word(0xd4)==71;
    if((pc!=0xc0ca79 && pc!=0xc0ca41) || (!pride && !graveyard && !exile && !hakuna && !adult) ||
       cpu->D || cpu->DB!=0x7e || cpu->PB!=0xc0 || cpu->m_flag || cpu->x_flag || cpu->_flag_D || (!adult && word(0xd0)!=(hakuna?450:graveyard?520:200)))return;
    unsigned actor=word(0x68),attribute=cpu->A;
    if(actor<0xb213 || actor>=0xc213 || ((actor-0xb213)&127))return;
    if((exile || hakuna || adult) && (actor!=0xb213 || pointer(actor+4)!=0xc5858a))return;
    if(pc==0xc0ca41) {
        if((!pride && !exile && !hakuna && !adult) || !TlkResourcesUseMd(adult?"gameplay.simba.adult_ceiling_rows":hakuna?"gameplay.levels.hakuna_matata.ceiling_clearance":exile?"gameplay.levels.simbas_exile.ceiling_clearance":"gameplay.levels.pride_lands.ceiling_clearance") || cpu->Y!=14)return;
        unsigned draw=word(actor+12),pose=pointer(0x7c),native,md;
        if(draw<0x8000 || draw>0xffe8 || pointer(draw+10)!=pose ||
           (adult && (word(draw+4)!=actor+8 || (g_ram[draw+9]&64))) ||
           !TlkHitboxDataGet(pose,actor!=0xb213,1,&native,&md) || cpu->A!=native)return;
        cpu->A=(uint16_t)md;cpu->_flag_N=!!(md&32768);cpu->_flag_Z=!md;cpu_mirrors_to_p(cpu);
        trace(cpu,pc,"clearance",pose,native,md);return;
    }
    if(!TlkResourcesUseMd(adult?"gameplay.simba.adult_ceiling_rows":hakuna?"gameplay.levels.hakuna_matata.ceiling_rows":exile?"gameplay.levels.simbas_exile.ceiling_rows":graveyard?"gameplay.levels.elephant_graveyard.ceiling_rows":"gameplay.levels.pride_lands.ceiling_rows") || word(0xa68e) || word(0xa690) || attribute>255 ||
       attribute>=0xb0 || (attribute>=0x40 && attribute<0x50))return;
    /* Original MD0028FE tests the lower row repeatedly, never the upper one.
     * All65536 original upper/lower attribute pairs prove this clear result
     * after the shared first lower-row check. Original STZ results and the
     * PLD/PLP/RTL epilogue own the return; no guest data or flags are written. */
    trace(cpu,pc,"rows",0,attribute,attribute);
    interp_bridge_pre_opcode_redirect(0xc0caf5);
}
void TlkCeilingInstall(void) {
    interp_bridge_add_pre_opcode_hook(0xc0ca79,pre);
    interp_bridge_add_pre_opcode_hook(0xc0ca41,pre);
}
