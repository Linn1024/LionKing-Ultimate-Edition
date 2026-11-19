#ifndef TLK_RNG_ENTRY_H
#define TLK_RNG_ENTRY_H
#include <stddef.h>
#include <stdint.h>
#include "cpu_state.h"
typedef struct TlkRngEntryData { uint32_t seed; int ready; } TlkRngEntryData;
int TlkRngEntryInit(TlkRngEntryData *,const uint8_t *,size_t,const uint8_t *,size_t);
/* Normal Pride entry only. CPU/history are read-only; no host pending state. */
int TlkRngEntryApply(const TlkRngEntryData *,const CpuState *,uint32_t,uint8_t *,size_t,int);
/* Preserve the existing stream on noninitial stage loads; no pending state. */
int TlkRngStagePreserve(CpuState *,uint32_t,const uint8_t *,size_t,int);
#endif
