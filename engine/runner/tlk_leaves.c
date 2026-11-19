#include "tlk_leaves.h"
#include "tlk_guest.h"
#include "tlk_resources.h"
#include "tlk_audio.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>

static int previous_source;
static unsigned word(unsigned a) { return g_ram[a]|(unsigned)g_ram[a+1]<<8; }
static int pride(void) { return !word(0x1ff9e) && (word(0xdf)==0x387 || word(0xdf)==0x80d); }
int TlkLeavesProfileChanged(void) {
    int source=TlkResourcesUseMd("gameplay.levels.pride_lands.leaves") |
        (TlkResourcesUseMd("gameplay.levels.simbas_exile.leaves")<<1);
    int changed=source!=previous_source;previous_source=source;return changed;
}
static RecompReturn original(CpuState *cpu,unsigned entry) {
    if (getenv("TLK_LEAF_ENTRY")) {
        fprintf(stderr,"leaf-entry %06x pb=%02x sp=%04x hrv=%u stack=",entry,cpu->PB,cpu->S,cpu->host_return_valid);
        for (unsigned i=1;i<=10;i++) fprintf(stderr,"%02x",g_ram[(cpu->S+i)&65535]);
        fprintf(stderr,"\n");
    }
    return TlkRunOriginal(cpu,entry,3);
}
RecompReturn TlkLeafEmitterDispatch(CpuState *cpu) { return original(cpu,0xc1fc36); }
RecompReturn TlkLeafParticleDispatch(CpuState *cpu) { return original(cpu,0xc1fd52); }
static void pre(CpuState *cpu,uint32_t pc) {
    int exile=word(0x1ff9e)==4 && word(0xdf)==0x44f && g_ram[0xe1]==0xc0;
    if ((!pride() && !exile) || cpu->m_flag || cpu->x_flag || cpu->DB!=0x7e) return;
    int behavior=(pride() && TlkResourcesUseMd("gameplay.levels.pride_lands.leaves")) ||
+        (exile && TlkResourcesUseMd("gameplay.levels.simbas_exile.leaves"));
    unsigned local=(cpu->D+0x18)&65535;
    const char *event=NULL;
    if ((pc&65535)==0xfcd4) {
        /* This byte is the original emitter's previous inside-trigger flag.
         * On this path it is zero and is dead before PLD/PLP/RTL. Reuse it
         * for one extra original spawn call, retaining its six-leaf cap.
         * Keeping the continuation in guest locals makes yields/saves safe. */
        if (!g_ram[local]) {
            TlkAudioLeafTrigger();event="trigger";
            if (behavior) {
                g_ram[local]=1;
                interp_bridge_pre_opcode_redirect((pc&0xff0000)|0xfcca);
            }
        } else if (behavior) event="third_spawn_return";
    } else if ((pc&65535)==0xfec1 && cpu->A==0x1800) {
        /* Original MD 19C886 integrates 0x1000 rather than SNES 0x1800.
         * Both immediates have identical N/Z, so existing flags remain valid. */
        if (behavior) cpu->A=0x1000;
        event="gravity";
    }
    static FILE *trace;
    const char *path=getenv("TLK_LEAF_TRACE");
    if (event && path) {
        if (!trace) { trace=fopen(path,"w");if(trace) fprintf(trace,"event,actor,local,count,value\n"); }
        if (trace) { fprintf(trace,"%s,%04x,%04x,%u,%u\n",event,word(0x68),cpu->D,word(0xa6be),cpu->A);fflush(trace); }
    }
}
void TlkLeavesInstall(void) {
    interp_bridge_add_pre_opcode_hook(0xc1fcd4,pre);
    interp_bridge_add_pre_opcode_hook(0xc1fec1,pre);
}
