#ifndef TLK_HUNT_DATA_H
#define TLK_HUNT_DATA_H
#include <stddef.h>
#include <stdint.h>
void TlkHuntDataClear(void);
int TlkHuntDataPrepare(const uint8_t *,size_t,const uint8_t *,size_t);
size_t TlkHuntDataSize(void);
int TlkHuntDataWrite(uint8_t *,size_t);
int TlkHuntDataRead(const uint8_t *,size_t,int);
int TlkHuntDataEntry(unsigned level,unsigned axis,unsigned *native,unsigned *md);
int TlkHuntDataMarker(unsigned cell,unsigned live,unsigned native,unsigned *md);
int TlkHuntDataTimer(unsigned field,unsigned *native,unsigned *md);
int TlkHuntDataOrigin(unsigned level,unsigned *md_y_offset);
#endif
