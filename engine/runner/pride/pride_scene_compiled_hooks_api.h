#ifndef PRIDE_SCENE_COMPILED_HOOKS_API_H
#define PRIDE_SCENE_COMPILED_HOOKS_API_H
#include "cpu_state.h"
#ifdef __cplusplus
extern "C" {
#endif
uint32_t PrideSceneCompiledPreOpcode(CpuState *cpu,uint32_t pc);
void PrideSceneCompiledUnmapped(CpuState *cpu,uint32_t source,uint32_t target);
#ifdef __cplusplus
}
#endif
#endif
