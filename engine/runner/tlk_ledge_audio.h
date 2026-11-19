#ifndef TLK_LEDGE_AUDIO_H
#define TLK_LEDGE_AUDIO_H
#include "cpu_state.h"
void TlkLedgeAudioInstall(unsigned frame);
RecompReturn TlkLedgeLeftDispatch(CpuState *cpu);
RecompReturn TlkLedgeRightDispatch(CpuState *cpu);
#endif
