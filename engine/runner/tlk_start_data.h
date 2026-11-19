#ifndef TLK_START_DATA_H
#define TLK_START_DATA_H
#include <stddef.h>
#include <stdint.h>
void TlkStartDataClear(void);
int TlkStartDataInit(const uint8_t *snes,size_t snes_size,const uint8_t *md,size_t md_size);
int TlkStartDataValue(unsigned axis,unsigned *native,unsigned *external);
int TlkStartDataGraveyardInputDelay(unsigned *native,unsigned *external);
/* Original MD post-rebuild retry control filter; normal entry is separate. */
int TlkStartDataRetryInputDelay(unsigned *native,unsigned *external);
int TlkStartDataGraveyardValue(unsigned axis,unsigned *native,unsigned *external);
int TlkStartDataCantWaitValue(unsigned axis,unsigned *native,unsigned *external);
/* Original normal-entry seed, prepared by the installer with entry positions. */
int TlkStartDataEntrySeed(unsigned *seed);
/* Bug Toss entry X/Y and right movement limit (axis2), prepared at install. */
int TlkStartDataBonusValue(unsigned axis,unsigned *native,unsigned *external);
size_t TlkStartDataRecordSize(void);
int TlkStartDataWrite(uint8_t *data,size_t size);
int TlkStartDataRead(const uint8_t *data,size_t size,int apply);
/* Normal world-coordinate stages4..9; Stampede3 has a special controller. */
int TlkStartDataLaterValue(unsigned level,unsigned axis,unsigned *native,unsigned *external);
#endif
