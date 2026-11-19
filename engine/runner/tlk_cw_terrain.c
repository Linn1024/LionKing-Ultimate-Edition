#include "tlk_cw_terrain.h"
#include "tlk_cw_terrain_data.h"
#include "tlk_next_scene_data.h"
#include "tlk_late_scene_data.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
extern void (*g_tlk_cw_terrain_pc_hook)(CpuState *,uint32_t);
static unsigned word(unsigned a){return g_ram[a]|(unsigned)g_ram[a+1]<<8;}
static unsigned pointer(unsigned a){return word(a)|(unsigned)g_ram[a+2]<<16;}
static const struct {unsigned pc,below,height,point,right;} loads[]={
    {0xc512,0,0,0},{0xc55b,1,0,0},{0xc51f,0,1,0},{0xc568,1,1,0},
    {0xc64a,1,0,0},{0xc6b7,0,0,0},{0xc734,1,0,0},{0xc797,0,0,0},
    {0xc7d0,0,0,0},{0xc8bb,0,0,0},{0xc934,0,0,0},{0xc9b6,0,0,0,1},
    {0xca5e,1,0,0},{0xca82,0,0,0},{0xcac3,0,0,0},{0x7a1c,0,1,1},{0xcbb1,0,1,2}
};
static void observe(CpuState *cpu,uint32_t pc){
    int exile=word(0x1ff9e)==4 && pointer(0xdf)==0xc0044f;
    int king=word(0x1ff9e)==1 && pointer(0xdf)==0xc003b9;
    int hakuna=word(0x1ff9e)==5 && pointer(0xdf)==0xc00481;
    int destiny=word(0x1ff9e)==6 && pointer(0xdf)==0xc004b3;
    int prepared=word(0x1ff9e)==7 && pointer(0xdf)==0xc004e5;
    int returning=word(0x1ff9e)==8 && pointer(0xdf)==0xc00517;
    int rock=word(0x1ff9e)==9 && pointer(0xdf)==0xc00549;
    unsigned row_bytes=returning?550:rock?200:prepared?610:destiny?604:hakuna?450:exile?200:800,rows=returning?43:rock?100:prepared?45:destiny?44:hakuna?71:exile?155:31,bytes=row_bytes*rows;
    if((!king && !exile && !hakuna && !destiny && !prepared && !returning && !rock) ||
       !TlkResourcesUseMd(returning?"gameplay.levels.simbas_return.terrain":rock?"gameplay.levels.pride_rock.terrain":prepared?"gameplay.levels.be_prepared.terrain":destiny?"gameplay.levels.simbas_destiny.terrain":hakuna?"gameplay.levels.hakuna_matata.terrain":exile?"gameplay.levels.simbas_exile.terrain":"gameplay.levels.cant_wait.terrain") ||
       (king?!TlkCwTerrainDataSize():(returning||rock)?!TlkLateSceneDataReady():!TlkNextSceneDataReady()) ||
       cpu->D || cpu->DB!=0x7e || (cpu->PB!=0xc0 && cpu->PB) || cpu->_flag_D ||
       word(0xd0)!=row_bytes || word(0xd4)!=rows)return;
    unsigned i;
    for(i=0;i<sizeof loads/sizeof *loads;i++)if((pc&65535)==loads[i].pc)break;
    if(i==sizeof loads/sizeof *loads)return;
    /* The wall classifier loads one byte after SEP #$20. All other seams
     * load words. Keep the original width, including A's hidden high byte. */
    if(cpu->m_flag!=(loads[i].pc==0xc7d0))return;
    /* C9B4 reads [DC],Y with Y=2. DC itself still names the current
     * cell; the prepared operand must come from its right neighbor. */
    unsigned base=pointer(0xe9),at=pointer(0xdc)+loads[i].below*row_bytes+loads[i].right*2;
    if(base<0x7e0000 || base>0x800000-bytes || at<base || at-base>=bytes || ((at-base)&1))return;
    unsigned cell=(at-base)/2,native_column=loads[i].height?word(loads[i].point==1?0x1f:0x46):0;
    /* C5C1 clobbers46 with the native quadrant index. MD2B8E retains
     * the full X&15 column for its point-height lookup. */
    unsigned column=loads[i].point==2?(word(0x4e)&15):native_column;
    unsigned native=cpu->A&255,external;
    if(returning||rock){
        if(!TlkLateSceneTerrain(returning?8:9,cell,word(at-0x7e0000),loads[i].height,native_column,column,native,&external))return;
    }else if(loads[i].point==2){
        if(king?!TlkCwTerrainDataPoint(cell,word(at-0x7e0000),native_column,column,native,&external):
           !TlkNextSceneTerrainPoint(prepared?7:destiny?6:hakuna?5:4,cell,word(at-0x7e0000),native_column,column,native,&external))return;
    }else if(king?!TlkCwTerrainDataGet(cell,word(at-0x7e0000),loads[i].height,column,native,&external):
       !TlkNextSceneTerrain(prepared?7:destiny?6:hakuna?5:4,cell,word(at-0x7e0000),loads[i].height,column,native,&external))return;
    /* Supply the selected original cell operand. The native lookup timing,
     * masks, contact test, floor delta and actor stores keep executing. */
    cpu->A=(loads[i].height || cpu->m_flag)?(cpu->A&0xff00)|external:external;
    unsigned mask=cpu->m_flag?255:65535,sign=cpu->m_flag?128:32768;
    cpu->_flag_N=!!(cpu->A&sign);cpu->_flag_Z=!(cpu->A&mask);cpu_mirrors_to_p(cpu);
    static FILE *trace[7];static int checked[7];unsigned scope=rock?6:returning?5:prepared?4:destiny?3:hakuna?2:exile?1:0;
    if(!checked[scope]){const char *p=getenv(rock?"TLK_PRIDE_ROCK_TERRAIN_TRACE":returning?"TLK_RETURN_TERRAIN_TRACE":prepared?"TLK_BE_PREPARED_TERRAIN_TRACE":destiny?"TLK_DESTINY_TERRAIN_TRACE":hakuna?"TLK_HAKUNA_TERRAIN_TRACE":exile?"TLK_EXILE_TERRAIN_TRACE":"TLK_CW_TERRAIN_TRACE");checked[scope]=1;if(p)trace[scope]=fopen(p,"w");
        if(trace[scope])fputs("field,pc,cell,column,height,native,md\n",trace[scope]);}
    if(trace[scope] && native!=external)fprintf(trace[scope],"%u,%06x,%u,%u,%u,%u,%u\n",snes_frame_counter+1,pc,cell,column,loads[i].height,native,external);
}
static void after(CpuState *cpu,uint32_t pc){observe(cpu,pc+2);}
void TlkCwTerrainInstall(void){
    g_tlk_cw_terrain_pc_hook=after;
    for(unsigned i=0;i<sizeof loads/sizeof *loads;i++){
        interp_bridge_add_pre_opcode_hook(0xc00000|loads[i].pc,observe);
        interp_bridge_add_pre_opcode_hook(loads[i].pc,observe);
    }
}
