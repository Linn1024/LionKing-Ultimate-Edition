/* PC sprite assembly is native C. Optional removal of the original CPU's
 * instruction-time bottleneck in the RAM-only object projection/OAM writers.
 * Keep NMI, hardware transfers, game logic, audio and explicit waits paced.
 * Force-include only when compiling the original C0 A000-A7FF render unit. */
#ifndef TLK_NATIVE_RENDER_PACE_H
#define TLK_NATIVE_RENDER_PACE_H
/* Preserve the generated unit's original header order. The AOT deadline
 * macro must not alter inline helpers parsed in common_cpu_infra.h. */
#include "pride_scene_compiled_hooks_api.h"
#include "tlk_native_hooks_api.h"
#include <stdio.h>
#include <stdlib.h>
#include "cpu_state.h"
#include "cpu_trace.h"
#include "common_cpu_infra.h"
#include "funcs.h"
#define AOT_PACE_GENERATED 1
#include "aot_pace.h"
#include "common_rtl.h"
extern int g_tlk_smooth_updates;
extern int g_tlk_main_update_field,g_tlk_render_world_ready,snes_frame_counter;
extern unsigned g_tlk_render_world_level;
extern const unsigned *g_tlk_live_update_serial;
extern unsigned g_tlk_update_start_serial;
extern int g_tlk_update_pending;
static inline int TlkNativeSpritePace(CpuState *cpu,uint32_t cyc,uint32_t mc,uint32_t pc) {
    /* Match the interpreter's draw-box observers. These run after LDA/LDY,
     * before the following bounds comparisons; no original instruction edits. */
    if((pc==0xc0a5e3 || pc==0xc0a5ed) && g_tlk_wide_pc_hook)
        g_tlk_wide_pc_hook(cpu,pc);
    /* After the original tile-cache/uploader selection, before its OAM budget
     * rejection. Read-only source intent gets actual preloaded tile indices. */
    if(pc==0xc0a6a2 && g_tlk_wide_pc_hook)g_tlk_wide_pc_hook(cpu,0xc0a6a4);
    if(g_tlk_smooth_updates && g_tlk_render_world_ready &&
       g_tlk_update_pending && g_tlk_live_update_serial &&
       ((pc>=0xc0a323 && pc<0xc0a3a9) || (pc>=0xc0a3c5 && pc<0xc0a50f) ||
        (pc>=0xc0a531 && pc<=0xc0a832)) && g_ram) {
        unsigned level=g_ram[0x1ff9e]|(unsigned)g_ram[0x1ff9f]<<8;
        unsigned scene=g_ram[0xdf]|(unsigned)g_ram[0xe0]<<8|(unsigned)g_ram[0xe1]<<16;
        unsigned health=g_ram[0x2004]|(unsigned)g_ram[0x2005]<<8;
        unsigned finished=g_ram[0xa6c2]|(unsigned)g_ram[0xa6c3]<<8;
        unsigned hazard=g_ram[0xa6ba]|(unsigned)g_ram[0xa6bb]<<8;
        unsigned action=g_ram[0xb243]|(unsigned)g_ram[0xb244]<<8|(unsigned)g_ram[0xb245]<<16;
        unsigned player=g_ram[0xb217]|(unsigned)g_ram[0xb218]<<8|(unsigned)g_ram[0xb219]<<16;
        int main_scene=level<10 && level!=3 && action>=0xc30000 && action<0xc40000 &&
            (scene==0xc00387+level*50 || (level==9 && scene==0xc007db));
        /* Timon's three Hunt layouts share the C56/C57 live controller. Wider
         * draw bounds can otherwise make RAM sprite assembly take two NMIs.
         * Only this same audited projection/OAM bookkeeping is shortened;
         * Hunt movement, catching, countdown, results and hardware keep their
         * original code and instruction timing. */
        int hunt_scene=level>=11 && level<=13 && scene==0xc005dd+(level-10)*50 &&
            player==0xc5858a && action>=0xc56000 && action<0xc58000;
        if((main_scene || hunt_scene) && level==g_tlk_render_world_level &&
           health>0 && health<100 && !finished && !hazard && !g_ram[0xa89] && !g_ram[0xa8a]) {
            /* OAM upload serials can change before this update finishes;
             * they cannot delimit native RAM-only sprite assembly work. */
            /* One virtual clock keeps progress monotonic; all original
             * register/RAM effects and recorded sprite pieces still execute. */
            mc=1;cyc=1;
        }
    }
    return aot_pace_point(cpu,cyc,mc,pc);
}
#define aot_pace_point TlkNativeSpritePace
#endif
