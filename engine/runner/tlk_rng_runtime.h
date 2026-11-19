#ifndef TLK_RNG_RUNTIME_H
#define TLK_RNG_RUNTIME_H
#include <stddef.h>
#include <stdint.h>
typedef struct CpuState CpuState;
void TlkRngRuntimeClear(void);
int TlkRngRuntimeInit(const uint8_t *,size_t,const uint8_t *,size_t);
int TlkRngRuntimeReady(void);
/* Advance the normal shared 24-bit game generator and return its real draw. */
unsigned TlkRngRuntimeNextValue(void);
void TlkRngRuntimeInstall(void);
void TlkRngStageBeginOpcode(CpuState *,uint32_t);
int TlkRngRuntimeProfileChanged(void);
#endif
