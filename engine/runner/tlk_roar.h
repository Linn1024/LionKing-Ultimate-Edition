#ifndef TLK_ROAR_H
#define TLK_ROAR_H
#include "cpu_state.h"
RecompReturn TlkRoarHandlerDispatch(CpuState *cpu);
void TlkRoarInstall(void);
int TlkRoarProfileChanged(void);
#endif
