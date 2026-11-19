#ifndef TLK_DESTINY_MONKEY_H
#define TLK_DESTINY_MONKEY_H
#include "cpu_state.h"
void TlkDestinyMonkeyInstall(void);
int TlkDestinyMonkeyHookSite(unsigned);
uint32_t TlkDestinyMonkeyOpcode(CpuState *,uint32_t);
#endif
