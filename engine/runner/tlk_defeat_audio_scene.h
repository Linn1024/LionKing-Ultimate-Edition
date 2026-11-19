#ifndef TLK_DEFEAT_AUDIO_SCENE_H
#define TLK_DEFEAT_AUDIO_SCENE_H
#include <stdint.h>
/* Shared defeat is an enemy program, not a first-level lizard-only effect. */
static inline int TlkDefeatAudioScene(const uint8_t *ram) {
    unsigned level=ram[0x1ff9e]|(unsigned)ram[0x1ff9f]<<8;
    unsigned descriptor=ram[0xdf]|(unsigned)ram[0xe0]<<8|(unsigned)ram[0xe1]<<16;
    return level<10 && (descriptor==0xc00387+level*0x32 || (!level && descriptor==0xc0080d));
}
#endif
