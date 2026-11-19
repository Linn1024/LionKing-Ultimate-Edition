#ifndef TLK_RNG_SCENE_H
#define TLK_RNG_SCENE_H
#include <stddef.h>
#include <stdint.h>
#include "cpu_state.h"
/* Caller supplies the verified original ROM pair. No mutable host continuation. */
typedef struct TlkRngSceneData { uint32_t normal_seed; int ready; } TlkRngSceneData;
int TlkRngSceneDataInit(TlkRngSceneData *,const uint8_t *,size_t,const uint8_t *,size_t);
/* Pre-opcode seams in original C07958. Not installed or advertised by itself. */
int TlkRngSceneStep(const TlkRngSceneData *,CpuState *,uint32_t,uint8_t *,size_t,int);
#endif
