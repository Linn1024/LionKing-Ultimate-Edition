#pragma once
#include <SDL3/SDL.h>
#ifdef __cplusplus
extern "C" {
#endif
void *TlkNativeAudioPreviewStart(unsigned level,char *reason,size_t size);
void *TlkNativeEffectPreviewStart(unsigned level,unsigned event,char *reason,size_t size);
/* A subject gallery always loads its own level, independent of the live game. */
void *TlkSubjectPreviewStart(const char *resource,unsigned scene,char *reason,size_t size);
/* Groups and unsupported subjects must not manufacture empty comparison cards. */
int TlkSubjectPreviewSupported(const char *resource);
int TlkSubjectPreviewPoll(void *job,Uint8 **pixels,Uint32 *bytes,unsigned *frames,char *reason,size_t size);
/* 0 preparing, 1 complete (SDL_free the samples), -1 unavailable. */
int TlkNativeAudioPreviewPoll(void *job,SDL_AudioSpec *spec,Uint8 **samples,Uint32 *bytes,char *reason,size_t size);
void TlkNativeAudioPreviewClose(void *job);
#ifdef __cplusplus
}
#endif
