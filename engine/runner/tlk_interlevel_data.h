#ifndef TLK_INTERLEVEL_DATA_H
#define TLK_INTERLEVEL_DATA_H
#include <stddef.h>
#include <stdint.h>
/* Prepared Pride completion illustration; no cartridge interpreter in playback. */
int TlkInterlevelDataPrepare(const uint8_t *,size_t,const uint8_t *,size_t);
void TlkInterlevelDataClear(void);
int TlkInterlevelDataReady(void);
size_t TlkInterlevelDataRecordSize(void);
int TlkInterlevelDataWrite(uint8_t *,size_t);
int TlkInterlevelDataRead(const uint8_t *,size_t,int);
int TlkInterlevelDataRender(unsigned tick,unsigned brightness,unsigned width,uint32_t *);
int TlkInterlevelDataRenderEnding(unsigned native_pose,unsigned brightness,unsigned width,uint32_t *);
int TlkInterlevelDataEndingTitleReady(void);
int TlkInterlevelDataRenderEndingTitle(unsigned brightness,unsigned width,uint32_t *);
int TlkInterlevelDataCreditsReady(void);
int TlkInterlevelDataRenderCredits(unsigned tick,unsigned brightness,unsigned width,uint32_t *);
int TlkInterlevelDataRenderFade(unsigned tick,unsigned cap,unsigned loss,unsigned width,uint32_t *);
unsigned TlkInterlevelDataEvents(unsigned tick);
unsigned TlkInterlevelDataDuration(void);
unsigned TlkInterlevelDataPose(unsigned program,unsigned tick);
const uint8_t *TlkInterlevelDataSample(unsigned sample,size_t *size,unsigned *period);
int TlkInterlevelDataCliffReady(void);
int TlkInterlevelDataTimonReady(void);
int TlkInterlevelDataTimonBankMatches(const uint8_t *,size_t);
int TlkInterlevelDataRenderTimon(unsigned,unsigned,int,int,int,int,int,unsigned,const uint16_t *,const uint8_t *,uint32_t *);
unsigned TlkInterlevelDataCliffEvents(unsigned tick);
unsigned TlkInterlevelDataCliffPose(unsigned program,unsigned tick);
int TlkInterlevelDataRenderCliff(unsigned tick,unsigned cap,unsigned loss,unsigned width,uint32_t *pixels);
#endif
