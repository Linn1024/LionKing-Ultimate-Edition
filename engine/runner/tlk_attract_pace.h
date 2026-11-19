/* One untouched generated demo unit, original header order preserved. */
#ifndef TLK_ATTRACT_PACE_H
#define TLK_ATTRACT_PACE_H
#include "tlk_native_hooks_api.h"
#include <stdio.h>
#include <stdlib.h>
#include "cpu_state.h"
#include "cpu_trace.h"
#include "common_cpu_infra.h"
#include "funcs.h"
#define AOT_PACE_GENERATED 1
#include "aot_pace.h"
void TlkAttractOpcode(CpuState *,uint32_t);
static inline int TlkAttractPace(CpuState *cpu,uint32_t cyc,uint32_t mc,uint32_t pc) {
    if(pc==0xc5012b)TlkAttractOpcode(cpu,0xc5012f);
    else if(pc==0xc501d4)TlkAttractOpcode(cpu,0xc501d6);
    else if(pc==0xc501e9)TlkAttractOpcode(cpu,0xc501eb);
    return aot_pace_point(cpu,cyc,mc,pc);
}
#define aot_pace_point TlkAttractPace
#endif
