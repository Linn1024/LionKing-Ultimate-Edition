/* Native sound request ownership; disabled in hosts without compiled hooks. */
#ifndef TLK_NATIVE_AUDIO_OWNER_H
#define TLK_NATIVE_AUDIO_OWNER_H
#include <stddef.h>
#include <stdint.h>
#include "cpu_state.h"
#ifndef TLK_NATIVE_AUDIO_OWNER_AVAILABLE
#define TLK_NATIVE_AUDIO_OWNER_AVAILABLE 0
#endif
#if TLK_NATIVE_AUDIO_OWNER_AVAILABLE
void TlkNativeAudioOwnerReset(void);
void TlkNativeAudioOwnerCpu(CpuState *cpu,uint32_t pc);
void TlkNativeAudioOwnerInstall(void);
void TlkNativeAudioOwnerSpc(unsigned pc,unsigned a,unsigned x,unsigned y,const uint8_t *ram);
void TlkNativeAudioOwnerLatchKon(unsigned value);
void TlkNativeAudioOwnerCommit(unsigned channel);
int TlkNativeAudioOwnerMute(unsigned channel,unsigned srcn,int echo);
int TlkNativeAudioOwnerMusicMute(unsigned channel,int echo_volume_l,int echo_volume_r);
size_t TlkNativeAudioOwnerStateSize(void);
int TlkNativeAudioOwnerSave(uint8_t *data,size_t size);
int TlkNativeAudioOwnerValidate(const uint8_t *data,size_t size);
int TlkNativeAudioOwnerLoad(const uint8_t *data,size_t size);
#else
static inline void TlkNativeAudioOwnerReset(void) {  }
static inline void TlkNativeAudioOwnerCpu(CpuState *cpu,uint32_t pc) {  }
static inline void TlkNativeAudioOwnerInstall(void) {  }
static inline void TlkNativeAudioOwnerSpc(unsigned pc,unsigned a,unsigned x,unsigned y,const uint8_t *ram) {  }
static inline void TlkNativeAudioOwnerLatchKon(unsigned value) {  }
static inline void TlkNativeAudioOwnerCommit(unsigned channel) {  }
static inline int TlkNativeAudioOwnerMute(unsigned channel,unsigned srcn,int echo) { return 0; }
static inline int TlkNativeAudioOwnerMusicMute(unsigned channel,int echo_volume_l,int echo_volume_r) { return 0; }
static inline size_t TlkNativeAudioOwnerStateSize(void) { return 0; }
static inline int TlkNativeAudioOwnerSave(uint8_t *data,size_t size) { return size==0; }
static inline int TlkNativeAudioOwnerValidate(const uint8_t *data,size_t size) { return size==0; }
static inline int TlkNativeAudioOwnerLoad(const uint8_t *data,size_t size) { return size==0; }
#endif
#endif
