#ifndef TLK_GRAVEYARD_DATA_H
#define TLK_GRAVEYARD_DATA_H
#include <stdint.h>
#include <stddef.h>
int TlkGraveyardDataPrepare(const uint8_t *,size_t,const uint8_t *,size_t);
size_t TlkGraveyardDataRecordSize(void);
int TlkGraveyardDataWrite(uint8_t *,size_t);
int TlkGraveyardDataRead(const uint8_t *,size_t,int);
int TlkGraveyardGroundTag(unsigned x,unsigned y,unsigned native_tag,const uint8_t *ram,unsigned *tag);
int TlkGraveyardDataReady(void);
int TlkGraveyardFarewellValue(unsigned cursor,unsigned width,unsigned *value);
int TlkGraveyardVultureLaunch(unsigned *native,unsigned *md);
int TlkGraveyardVultureTurn(unsigned left,unsigned *native,unsigned *md);
int TlkGraveyardHeadSurface(unsigned index,unsigned live,unsigned *md);
/* Countdown, random offset mask and original saved X/Y actor offsets. */
const uint16_t *TlkGraveyardShakeRules(void);
int TlkGraveyardBoneMarker(unsigned cell,unsigned live,unsigned native,unsigned *md);
int TlkGraveyardRevealMarker(unsigned cell,unsigned live,unsigned native,unsigned *md);
int TlkGraveyardDeathPose(unsigned age,unsigned *pose);
int TlkGraveyardBoneContact(unsigned pose,unsigned component,unsigned index,unsigned *native,unsigned *md);
int TlkGraveyardBoneContactDelay(unsigned *delay);
int TlkGraveyardVultureMarker(unsigned cell,unsigned live,unsigned native,unsigned *md);
int TlkGraveyardPickupMarker(unsigned cell,unsigned live,unsigned native,unsigned *md);
int TlkGraveyardBugMarker(unsigned cell,unsigned live,unsigned native,unsigned *md);
/* Native Y offset, MD Y subtraction, signed left/right X probe arguments. */
const uint16_t *TlkGraveyardWallRules(void);
int TlkGraveyardPerchedMarker(unsigned cell,unsigned live,unsigned native,unsigned *md);
int TlkGraveyardUpperMarker(unsigned marker,unsigned cell,unsigned live,unsigned native,unsigned *md);

/* Original MD CRAM words for farewell indices8..15; installer-prepared. */
int TlkGraveyardFarewellPalette(uint16_t colors[8]);

#endif
