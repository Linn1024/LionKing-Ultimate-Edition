#ifndef TLK_SPAWN_INIT_H
#define TLK_SPAWN_INIT_H
#include "cpu_state.h"
void TlkSpawnInitInstall(void);
RecompReturn TlkSpawnInitialDispatch(CpuState *cpu);
RecompReturn TlkSpawnStreamDispatch(CpuState *cpu);
RecompReturn TlkSpawnCameraReturnDispatch(CpuState *cpu);
RecompReturn TlkSpawnScanDispatch(CpuState *cpu);
#endif
