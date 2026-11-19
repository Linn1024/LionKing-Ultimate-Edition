#include "tlk_porcupine_attack.h"
uint32_t TlkPorcupineAttackBoundary(uint32_t pc,uint16_t timer,uint16_t *phase) {
    switch(pc) {
    case 0xc15c64: /* Skip native pre-movement contact and sound. */
        *phase=0;return 0xc15cb2;
    case 0xc15d00: /* Original movement has finished. Test original contact once. */
        if(*phase==2) {*phase=0;return 0;}
        *phase=1;return 0xc15c78;
    case 0xc15c8f: /* Original contact/reaction return to the late phase. */
        if(*phase==1) {*phase=2;return 0xc15d00;}
        return 0;
    case 0xc15d14: /* Native code has now cleared nonpersistent timers. */
        if(timer==28) {*phase=3;return 0xc15ca6;}
        return 0;
    case 0xc15cb2: /* Original sound call/stack cleanup finished. */
        if(*phase==3) {*phase=0;return 0xc15d19;}
        return 0;
    default:return 0;
    }
}
