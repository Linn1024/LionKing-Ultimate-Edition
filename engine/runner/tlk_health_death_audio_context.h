#ifndef TLK_HEALTH_DEATH_AUDIO_CONTEXT_H
#define TLK_HEALTH_DEATH_AUDIO_CONTEXT_H
#include <stdint.h>
/* Source5114: shared timed-animation C30792 owns the health-death wrapper
 * before bank initialization, then its exact cub/adult drawing stream.
 * Caller separately validates scene, age, health and remaining lives. */
static unsigned TlkHealthDeathAudioAddress(const uint8_t *ram,unsigned at) {
    return ram[at]|(unsigned)ram[at+1]<<8|(unsigned)ram[at+2]<<16;
}
static int TlkHealthDeathAudioNested(const uint8_t *ram,int adult) {
    /* A blocking animation can retain its enclosing ledge/ostrich action.
     * The exact child program identifies death in those paths too. Callers
     * still require this scene's defeated player and remaining lives. */
    if(TlkHealthDeathAudioAddress(ram,0xb217)!=0xc5858a ||
       ram[0xa6ba] || ram[0xa6bb])return 0;
    unsigned child=TlkHealthDeathAudioAddress(ram,0xb221);
    if(child==(adult?0xc0e0c8u:0xc0e0a8u))return 1;
    if(child!=0xc0ea93)return 0;
    unsigned parent=TlkHealthDeathAudioAddress(ram,0xb225);
    unsigned first=adult?0xc0ebb8:0xc0ebf0,last=adult?0xc0ebe8:0xc0ec70;
    return parent>=first && parent<=last && !((parent-first)&3);
}
#endif
