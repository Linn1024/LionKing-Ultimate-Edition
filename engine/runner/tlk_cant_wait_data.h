#ifndef TLK_CANT_WAIT_DATA_H
#define TLK_CANT_WAIT_DATA_H
#include <stddef.h>
#include <stdint.h>
void TlkCantWaitDataClear(void);
int TlkCantWaitDataInit(const uint8_t *,size_t,const uint8_t *,size_t);
int TlkCantWaitExitBoundary(unsigned *native,unsigned *external);
int TlkCantWaitMonkeyGrip(unsigned pose,unsigned axis,unsigned *native,unsigned *external);
int TlkCantWaitRoarRange(unsigned *native,unsigned *external);
int TlkCantWaitHippoOffset(unsigned *native,unsigned *external);
int TlkCantWaitGiraffeOffset(unsigned *native,unsigned *external);
int TlkCantWaitOstrichDelay(unsigned *native,unsigned *external);
/*0: loop width,1: obstacle spawn distance,2: forward camera look. */
int TlkCantWaitRideValue(unsigned index,unsigned *native,unsigned *external);
int TlkCantWaitRideEvent(unsigned native_cursor,unsigned *distance,unsigned *flags);
size_t TlkCantWaitDataRecordSize(void);
int TlkCantWaitDataWrite(uint8_t *,size_t);
int TlkCantWaitDataRead(const uint8_t *,size_t,int apply);
#endif
