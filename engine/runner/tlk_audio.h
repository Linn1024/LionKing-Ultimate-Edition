#ifndef TLK_AUDIO_H
#define TLK_AUDIO_H
#include <stdint.h>
#include <stddef.h>
#include "cpu_state.h"
void TlkAudioInstall(void);
void TlkAudioHyenaBattleJump(CpuState *cpu,uint32_t pc);
void TlkAudioPorcupineAttackVoice(CpuState *cpu,uint32_t pc);
void TlkAudioFrame(unsigned frame);
struct TlkFinalArt;
void TlkAudioSetSoundTestAssets(const struct TlkFinalArt *);
/* Original animation token boundary, shared by compiled and interpreter paths. */
void TlkAudioAnimationToken(CpuState *cpu,uint32_t pc);
int TlkAudioGraveyardScene(void);
void TlkAudioMix(int16_t *samples,unsigned count,unsigned rate);
int TlkAudioProfileChanged(void);
int TlkAudioMusicAvailable(const char *id);
int TlkAudioNativeMusicSelected(void);
int TlkEndingTitleActive(void);
int TlkEndingCreditsTick(void);
void TlkAudioReset(void);
/* Called before initial load. Headless keeps the fraction without a device. */
void TlkAudioBindHost(double *sample_fraction,unsigned output_rate);
size_t TlkAudioHistorySize(void);
int TlkAudioSaveHistory(uint8_t *out,size_t size);
int TlkAudioValidateHistory(const uint8_t *data,size_t size);
int TlkAudioLoadHistory(const uint8_t *data,size_t size);
#define TLK_AUDIO_HISTORY_MAX (9u*1024u*1024u)
void TlkAudioLeafTrigger(void);
/* The original actor owns pulse timing; this only selects its adult voice. */
void TlkAudioAdultRoarPulse(CpuState *cpu,uint32_t pc);
void TlkAudioBePreparedGroupCall(unsigned actor);
void TlkAudioDestinyMonkeyShot(void);
int TlkAudioHyenaTauntTrigger(void);
void TlkAudioAdultHyenaTauntEntry(CpuState *cpu,uint32_t pc);
int TlkAudioHyenaVoiceTrigger(void);
int TlkAudioLizardDefeatTrigger(void);
int TlkAudioPickupArrivalTrigger(void);
int TlkAudioLedgeGrabTrigger(void);
int TlkAudioLizardLaunchTrigger(void);
int TlkAudioLizardAttackTrigger(void);
extern void (*g_tlk_audio_pc_hook)(CpuState *cpu, uint32_t pc);
#endif
