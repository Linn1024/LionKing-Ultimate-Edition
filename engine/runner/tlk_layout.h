#ifndef TLK_LAYOUT_H
#define TLK_LAYOUT_H
#include "cpu_state.h"
RecompReturn TlkMarkerDispatch(CpuState *cpu);
void TlkLayoutInstall(void);
int TlkLayoutProfileChanged(void);
void TlkLayoutBonusPreOpcode(CpuState *,uint32_t);
/* Existing selected MD retry input filter, before the shared marker clear. */
void TlkLayoutRetryPreOpcode(CpuState *,uint32_t);
#endif
