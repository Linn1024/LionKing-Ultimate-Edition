#ifndef TLK_HYENA_PROBE_H
#define TLK_HYENA_PROBE_H
#include "cpu_state.h"
void TlkHyenaWalkingProbe(CpuState *cpu,uint32_t pc);
void TlkHyenaProbePrepareSource(void);
int TlkHyenaProbeProfileChanged(void);
#endif
