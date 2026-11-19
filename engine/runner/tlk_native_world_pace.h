/* Apply the same reviewed RAM-work budget to compiled and interpreted code.
 * Include before the unchanged generated packet/scheduler/cache units. */
#ifndef TLK_NATIVE_WORLD_PACE_H
#define TLK_NATIVE_WORLD_PACE_H
#include "pride_scene_compiled_hooks_api.h"
#include "tlk_native_hooks_api.h"
#include "cpu_state.h"
#include "cpu_trace.h"
#include "common_cpu_infra.h"
#include "funcs.h"
#define AOT_PACE_GENERATED 1
#include "aot_pace.h"
#include "common_rtl.h"
#include <stdint.h>
extern uint64_t TlkNativeUpdateMasterBudget(unsigned,unsigned,uint64_t);
static inline int TlkNativeWorldPace(CpuState *cpu,uint32_t cyc,uint32_t mc,uint32_t pc) {
    uint64_t budget=TlkNativeUpdateMasterBudget(pc,cpu->DB,mc);
    if(budget<mc){mc=(uint32_t)budget;cyc=1;}
    return aot_pace_point(cpu,cyc,mc,pc);
}
#define aot_pace_point TlkNativeWorldPace
#endif
