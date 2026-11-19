#ifndef TLK_TERRAIN_H
#define TLK_TERRAIN_H
#include "cpu_state.h"
RecompReturn TlkTerrainFloorDispatch(CpuState *cpu);
RecompReturn TlkTerrainRightDispatch(CpuState *cpu);
RecompReturn TlkTerrainRightActorDispatch(CpuState *cpu);
RecompReturn TlkTerrainLeftDispatch(CpuState *cpu);
RecompReturn TlkTerrainLeftActorDispatch(CpuState *cpu);
RecompReturn TlkTerrainWallDispatch(CpuState *cpu);
RecompReturn TlkTerrainLedgeDispatch(CpuState *cpu);
RecompReturn TlkTerrainCeilingDispatch(CpuState *cpu);
void TlkTerrainInstall(void);
int TlkTerrainProfileChanged(void);
#endif
