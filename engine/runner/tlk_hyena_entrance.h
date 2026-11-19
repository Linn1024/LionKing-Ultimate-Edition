#ifndef TLK_HYENA_ENTRANCE_H
#define TLK_HYENA_ENTRANCE_H
#include "cpu_state.h"
void TlkHyenaEntranceWindow(CpuState *cpu,uint32_t pc);
void TlkHyenaEntrancePrepareSource(void);
int TlkHyenaEntranceProfileChanged(void);
#endif
