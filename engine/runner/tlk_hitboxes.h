#ifndef TLK_HITBOXES_H
#define TLK_HITBOXES_H
#include "cpu_state.h"
void TlkHitboxesInstall(void);
void TlkTailContactPostOpcode(CpuState *cpu,uint32_t pc);
RecompReturn TlkBodyBoundsDispatch(CpuState *cpu);
RecompReturn TlkPlayerBoundsDispatch(CpuState *cpu);
void TlkAdultPointsPostOpcode(CpuState *cpu,uint32_t pc);
#endif
