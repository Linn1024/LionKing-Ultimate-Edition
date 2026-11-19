#ifndef TLK_PICKUP_AUDIO_H
#define TLK_PICKUP_AUDIO_H
#include "cpu_state.h"
void TlkPickupAudioInstall(unsigned frame);
RecompReturn TlkPickupArrivalDispatch(CpuState *cpu);
#endif
