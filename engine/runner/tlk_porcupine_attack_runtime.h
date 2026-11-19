#ifndef TLK_PORCUPINE_ATTACK_RUNTIME_H
#define TLK_PORCUPINE_ATTACK_RUNTIME_H
#include "cpu_state.h"
#include <stdint.h>
int TlkPorcupineAttackSelected(void);
int TlkPorcupineAttackProfileChanged(void);
uint32_t TlkPorcupineAttackOpcode(CpuState *,uint32_t);
#endif
