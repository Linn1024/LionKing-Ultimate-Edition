#include "tlk_rng_runtime.h"
#include "tlk_rng_entry.h"
#include "tlk_start_data.h"
#include "tlk_resources.h"
#include "tlk_guest.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static TlkRngEntryData entry_data;
static int previous_source;
unsigned TlkRngRuntimeNextValue(void) {
    /* Original C0CBBA / MD000B28, source-equivalent arithmetic. The caller
     * must use the returned value for its actual game decision or movement. */
    unsigned low=g_ram[0x1e00],middle=g_ram[0x1e01],high=g_ram[0x1e02];
    unsigned next_high=((high<<1)|((low>>1)&1))&255;
    unsigned next_middle=((middle<<1)|(high>>7))&255;
    unsigned difference=((low>>2)-low-(1-(middle>>7)))&255;
    unsigned next_low=(low>>1)|((difference&1)<<7);
    g_ram[0x1e00]=(uint8_t)next_low;g_ram[0x1e01]=(uint8_t)next_middle;g_ram[0x1e02]=(uint8_t)next_high;
    return next_low^next_middle;
}
void TlkRngRuntimeClear(void) { memset(&entry_data,0,sizeof entry_data);previous_source=0; }
int TlkRngRuntimeInit(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn) { return TlkRngEntryInit(&entry_data,s,sn,m,mn); }
int TlkRngRuntimeReady(void) {
    unsigned seed;
    if(TlkStartDataEntrySeed(&seed)){entry_data.seed=seed;entry_data.ready=1;}
    return entry_data.ready;
}
int TlkRngRuntimeProfileChanged(void) {
    int selected=TlkResourcesUseMd("gameplay.levels.pride_lands.random_entry") |
        (TlkResourcesUseMd("gameplay.scene_random_state")<<1);
    int changed=selected!=previous_source;previous_source=selected;return changed;
}
static void entry_opcode(CpuState *cpu,uint32_t pc) {
    if(!TlkRngRuntimeReady())return;
    if(pc==0xc08808){TlkRngStageBeginOpcode(cpu,pc);return;}
    if(TlkRngStagePreserve(cpu,pc,g_ram,0x20000,TlkResourcesUseMd("gameplay.scene_random_state"))){
        const char *path=getenv("TLK_RNG_SCENE_TRACE");static FILE *file;
        if(path && !file){file=fopen(path,"w");if(file)fputs("field,level,seed\n",file);}
        if(file){fprintf(file,"%u,%u,%06x\n",(unsigned)snes_frame_counter+1,g_ram[0x1ff9e]|g_ram[0x1ff9f]<<8,
            g_ram[0x1e00]|g_ram[0x1e01]<<8|g_ram[0x1e02]<<16);fflush(file);}
        return;
    }
    unsigned before=g_ram[0x1e00]|(unsigned)g_ram[0x1e01]<<8|(unsigned)g_ram[0x1e02]<<16;
    int changed=TlkRngEntryApply(&entry_data,cpu,pc,g_ram,0x20000,TlkResourcesUseMd("gameplay.levels.pride_lands.random_entry"));
    if(changed) {
        static FILE *trace;static int opened;
        if(!opened) { const char *path=getenv("TLK_RNG_ENTRY_TRACE");opened=1;if(path)trace=fopen(path,"w");
            if(trace)fprintf(trace,"field,before,selected,level,descriptor\n"); }
        if(trace) { fprintf(trace,"%u,%06x,%06x,%u,%06x\n",(unsigned)snes_frame_counter+1,before,entry_data.seed,
            g_ram[0x1ff9e]|(unsigned)g_ram[0x1ff9f]<<8,g_ram[0xdf]|(unsigned)g_ram[0xe0]<<8|(unsigned)g_ram[0xe1]<<16);fflush(trace); }
    }
}
void TlkRngRuntimeInstall(void) {
    interp_bridge_add_pre_opcode_hook(0xc07970,entry_opcode);
    interp_bridge_add_pre_opcode_hook(0xc07979,entry_opcode);
    interp_bridge_add_pre_opcode_hook(0xc08808,entry_opcode);
}
void TlkRngStageBeginOpcode(CpuState *cpu,uint32_t pc){
    unsigned level=g_ram[0x1ff9e]|g_ram[0x1ff9f]<<8;
    if(pc!=0xc08808 || !level || level>13 || !TlkRngRuntimeReady() ||
       !TlkResourcesUseMd("gameplay.scene_random_state") || cpu->PB!=0xc0 || cpu->DB || cpu->D ||
       cpu->m_flag || !cpu->x_flag || g_ram[0x1ffa2] || g_ram[0x1ffa3] || g_ram[0xe1]!=0xc0)return;
    /* MD1D77DE follows actor initialization and precedes gameplay pad reads.
     * Keep the incoming stream for actor setup, then use the prepared seed. */
    unsigned seed=entry_data.seed;
    g_ram[0x1e00]=seed;g_ram[0x1e01]=seed>>8;g_ram[0x1e02]=seed>>16;
    const char *path=getenv("TLK_RNG_STAGE_BEGIN_TRACE");static FILE *file;
    if(path && !file){file=fopen(path,"w");if(file)fputs("field,level,seed\n",file);}
    if(file){fprintf(file,"%u,%u,%06x\n",(unsigned)snes_frame_counter+1,level,seed);fflush(file);}
}
RecompReturn TlkRngEntryDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0x7958,2); }
