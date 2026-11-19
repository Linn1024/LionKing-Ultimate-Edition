#ifndef TLK_PORCUPINE_ATTACK_H
#define TLK_PORCUPINE_ATTACK_H
#include <stdint.h>
/* Phase is an action-local saved guest word, never a host episode flag. */
uint32_t TlkPorcupineAttackBoundary(uint32_t pc,uint16_t timer,uint16_t *phase);
#endif
