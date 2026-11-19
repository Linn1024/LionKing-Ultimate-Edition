#ifndef TLK_LEAVES_H
#define TLK_LEAVES_H
#include "cpu_state.h"
RecompReturn TlkLeafEmitterDispatch(CpuState *cpu);
RecompReturn TlkLeafParticleDispatch(CpuState *cpu);
void TlkLeavesInstall(void);
int TlkLeavesProfileChanged(void);
#endif
