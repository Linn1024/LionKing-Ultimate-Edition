#ifndef TLK_CANT_WAIT_GAMEPLAY_H
#define TLK_CANT_WAIT_GAMEPLAY_H
#include <stdint.h>
typedef struct CpuState CpuState;
void TlkCantWaitGameplayInstall(void);
void TlkCantWaitMonkeyGripPostOpcode(CpuState *,uint32_t);
void TlkCantWaitRoarPostOpcode(CpuState *,uint32_t);
void TlkCantWaitGiraffePostOpcode(CpuState *,uint32_t);
void TlkCantWaitOstrichDelayPostOpcode(CpuState *,uint32_t);
void TlkCantWaitRidePostOpcode(CpuState *,uint32_t);
#endif
