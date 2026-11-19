#ifndef TLK_HYENA_AUDIO_H
#define TLK_HYENA_AUDIO_H
#include "cpu_state.h"
#include "tlk_hyena_voice_policy.h"
void TlkHyenaAudioInstall(unsigned frame);
void TlkHyenaVoiceEntry(CpuState *cpu,uint32_t pc);
RecompReturn TlkHyenaTauntDispatch(CpuState *cpu);
#endif
