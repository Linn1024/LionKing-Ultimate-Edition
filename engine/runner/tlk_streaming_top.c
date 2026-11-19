#include "tlk_streaming_top.h"
#include "tlk_resources.h"
#include "tlk_guest.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "cpu_state.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static void pre(CpuState *cpu,uint32_t pc) {
    int pride=!word(0x1ff9e) && (word(0xdf)==0x387 || word(0xdf)==0x80d) && word(0xd0)==200 && word(0xd4)==80;
    int hakuna=word(0x1ff9e)==5 && word(0xdf)==0x481 && word(0xd0)==450 && word(0xd4)==71;
    int graveyard=word(0x1ff9e)==2 && word(0xdf)==0x3eb && word(0xd0)==520 && word(0xd4)==48;
    int prepared=word(0x1ff9e)==7 && word(0xdf)==0x4e5 && word(0xd0)==610 && word(0xd4)==45;
    const char *choice=graveyard?"gameplay.levels.elephant_graveyard.streaming_top":prepared?"gameplay.levels.be_prepared.streaming_top":hakuna?"gameplay.levels.hakuna_matata.streaming_top":"gameplay.levels.pride_lands.streaming_top";
    if(pc!=0xc0b93f || (!pride && !graveyard && !hakuna && !prepared) || !TlkResourcesUseMd(choice) || g_ram[0xe1]!=0xc0 ||
       cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
       word(0x68)!=0xb293 || cpu->S>0x1ffd || word(cpu->S+1)!=0xb617)return;
    unsigned row=word(0x48),top=row>12?row-12:0;
    if((row&1) || row>=word(0xd4)*2 || cpu->A!=top)return;
    /* Original MD09270A returns the clamped top index to its queue scanner.
     * Native C0B8EA already computes it here for culling but leaves $48 at
     * the camera row. Store the same result for subsequent original scans.
     * C0B93F ASL onward still owns culling arithmetic and CPU flags. The
     * B617 caller guard leaves the independent initial full scan unchanged. */
    g_ram[0x48]=(uint8_t)top;g_ram[0x49]=(uint8_t)(top>>8);
    static FILE *trace;static int opened;
    if(!opened) { const char *path=getenv("TLK_STREAMING_TOP_TRACE");opened=1;if(path)trace=fopen(path,"w");
        if(trace)fprintf(trace,"frame,pc,camera_x,camera_y,native_top,selected_top\n"); }
    if(trace) { fprintf(trace,"%d,%06x,%u,%u,%u,%u\n",snes_frame_counter,pc,word(0xb29b),word(0xb29d),row,top);fflush(trace); }
}
void TlkStreamingTopInstall(void) { interp_bridge_add_pre_opcode_hook(0xc0b93f,pre); }
RecompReturn TlkStreamingWindowDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc0b8ea,2); }
