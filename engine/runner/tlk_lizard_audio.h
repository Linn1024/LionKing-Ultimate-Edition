#ifndef TLK_LIZARD_AUDIO_H
#define TLK_LIZARD_AUDIO_H
#include "cpu_state.h"
#include "tlk_lizard_voice_policy.h"
void TlkLizardAttackVoice(CpuState *cpu,uint32_t pc);
void TlkLizardAudioInstall(unsigned frame);
RecompReturn TlkLizardDefeatDispatch(CpuState *cpu);
RecompReturn TlkLizardLaunchDispatch(CpuState *cpu);
#endif
