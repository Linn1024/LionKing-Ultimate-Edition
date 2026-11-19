#include "tlk_spawn_init.h"
#include "tlk_resources.h"
#include "tlk_guest.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>

static unsigned word(unsigned a) { return g_ram[a]|(unsigned)g_ram[a+1]<<8; }
static void put(unsigned a,unsigned v) { g_ram[a]=v;g_ram[a+1]=v>>8; }
static unsigned stack(CpuState *cpu,unsigned n) { return word(cpu->S+n); }
static int active(CpuState *cpu) {
    return TlkResourcesUseMd("gameplay.levels.pride_lands.activation") &&
        !word(0x1ff9e) && word(0xdf)==0x387 && g_ram[0xe1]==0xc0 &&
        !cpu->D && cpu->DB==0x7e && cpu->PB==0xc0 && !cpu->m_flag && cpu->x_flag &&
        cpu->S>=32 && cpu->S<=0x1ffd;
}
static void push(CpuState *cpu,unsigned v) { g_ram[cpu->S--]=(uint8_t)v; }
static void push_word(CpuState *cpu,unsigned v) { push(cpu,v>>8);push(cpu,v); }
static void trace(CpuState *cpu,const char *event) {
    static FILE *file;static int initialized;
    if(!initialized) { const char *p=getenv("TLK_SPAWN_INIT_TRACE");initialized=1;if(p)file=fopen(p,"w");
        if(file)fprintf(file,"event,frame,stack,camera_x,camera_y,actor,left,right,axis,count\n"); }
    if(file) { fprintf(file,"%s,%d,%04x,%u,%u,%04x,%u,%u,%u,%u\n",event,snes_frame_counter,cpu->S,
        word(0xb29b),word(0xb29d),word(0x68),word(0x46),word(0x14),word(0x48),word(0x16));fflush(file); }
}
static int late_scan(CpuState *cpu,unsigned return_offset,unsigned camera_offset) {
    return stack(cpu,return_offset)==0xb69e && stack(cpu,camera_offset)==0x8763 &&
           g_ram[cpu->S+camera_offset+2]==0xc0;
}
static void pre(CpuState *cpu,uint32_t pc) {
    if(!active(cpu))return;
    switch(pc&65535) {
    case 0xb8b9:
        if(stack(cpu,1)==0x86db && word(0x68)==0xb293) {
            trace(cpu,"defer_initial");interp_bridge_pre_opcode_redirect(0xc0b8e9);
        }
        break;
    case 0xb5fd:
        if(cpu->S<=0x1ffc && stack(cpu,1)==0x8773 && g_ram[cpu->S+3]==0xc0 &&
           word(0x68)==word(0xa3a) && word(word(0x68)+8)==0xb293) {
            trace(cpu,"defer_stream");interp_bridge_pre_opcode_redirect(0xc0b6a6);
        }
        break;
    case 0xb3cb:
        if(cpu->S>0x1ff8 || stack(cpu,1)!=0x8763 || g_ram[cpu->S+3]!=0xc0 || word(0x68)!=0xb293 ||
           stack(cpu,4)!=word(0xb29d) || stack(cpu,6)!=word(0xb29b))break;
        /* The original loader already saved X/Y on its guest stack. Once its
         * camera is stationary, run the original full scanner before this RTL.
         * The existing B69F cleanup restores $68, DB and P, then consumes the
         * real camera RTL frame. Every continuation lives on the guest stack,
         * including across interpreted yields and new-process saved states. */
        trace(cpu,"activate_settled");cpu_mirrors_to_p(cpu);
        push(cpu,cpu->P);push(cpu,cpu->DB);push_word(cpu,word(0x68));push_word(cpu,0xb69e);
        cpu->host_return_valid=2;interp_bridge_pre_opcode_redirect(0xc0b8b9);
        break;
    case 0xb8c6: {
        if(cpu->S>0x1ff4 || !late_scan(cpu,3,9) || word(0x68)!=0xb293)break;
        unsigned left=word(0x46),right=word(0x14),row=word(0x48),bottom=word(0x16);
        if(left>right || right>=word(0xd0) || row>bottom || bottom>=word(0xd4)*2)break;
        unsigned top=row>12?row-12:0;
        unsigned columns=word(0x52),rows=word(0x54);
        if(columns!=0xe4c1 || rows!=columns+word(0xd0))break;
        /* MD's initial rectangle is scanned by columns. Reuse the native
         * column scanner and its two linked queue indexes, rather than using
         * B8B9's original camera-zero row-loop assumptions at a nonzero Y. */
        put(0x46,top);put(0x14,bottom);put(0x48,left);put(0x16,right-left);
        put(0x52,rows);put(0x54,columns);trace(cpu,"column_rectangle");
        break;
    }
    case 0xb97b:
        if(cpu->S<=0x1fee && stack(cpu,1)==0xb8d6 && late_scan(cpu,9,15)) {
            trace(cpu,"scan_column");
            interp_bridge_pre_opcode_redirect(0xc0ba3f);
        }
        break;
    }
}
void TlkSpawnInitInstall(void) {
    const unsigned pcs[]={0xb8b9,0xb5fd,0xb3cb,0xb8c6,0xb97b};
    for(unsigned i=0;i<sizeof pcs/sizeof pcs[0];i++)interp_bridge_add_pre_opcode_hook(0xc00000|pcs[i],pre);
}
/* Forwarding entries retain the original byte programs and their hardware
 * return frames, so the same opcode seams apply in both execution modes. */
RecompReturn TlkSpawnInitialDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xb8b9,2); }
RecompReturn TlkSpawnStreamDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xb5fd,3); }
RecompReturn TlkSpawnCameraReturnDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xb3ca,3); }
RecompReturn TlkSpawnScanDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xb97b,2); }
