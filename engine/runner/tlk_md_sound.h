#ifndef TLK_MD_SOUND_H
#define TLK_MD_SOUND_H
#include <stddef.h>
#include <stdint.h>
/* Original MD sound driver, isolated from gameplay in the optional reference
 * library. ROM input must already have passed the resource loader's SHA check. */
int TlkMdSoundInit(const uint8_t *rom,size_t size);
void TlkMdSoundClose(void);
int TlkMdSoundReady(void);
const char *TlkMdSoundStatus(void);
void TlkMdSoundCommand(unsigned selector,unsigned value);
/* Original selector19 request with its explicit source D1 parameter. */
void TlkMdSoundPcm(unsigned sample,unsigned parameter);
/* Two reviewed Pride interlevel sample spans, using the original audio driver. */
void TlkMdSoundInterlevelSample(unsigned sample);
void TlkMdSoundInterlevelStop(void);
void TlkMdSoundBonusResultSample(void);
void TlkMdSoundCliffSample(void);
void TlkMdSoundCliffStop(void);
/* Original Exile outro calls1CAF9A/1CAFB0, isolated from level music. */
void TlkMdSoundExileExitSample(unsigned sample);
/* Original opening Timon raw PCM2D191E/319A, period125. */
void TlkMdSoundOpeningTimonSample(void);
void TlkMdSoundClearOutput(void);
void TlkMdSoundRestart(void);
int TlkMdSoundRender(int16_t *dst,unsigned frames,unsigned output_rate);
size_t TlkMdSoundStateSize(void);
int TlkMdSoundSaveState(uint8_t *out,size_t size);
int TlkMdSoundValidateState(const uint8_t *data,size_t size);
int TlkMdSoundLoadState(const uint8_t *data,size_t size);
#endif
