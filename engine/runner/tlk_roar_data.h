#ifndef TLK_ROAR_DATA_H
#define TLK_ROAR_DATA_H
#include <stddef.h>
#include <stdint.h>
#define TLK_ROAR_STREAM 0xc0f006u
void TlkRoarDataClear(void);
int TlkRoarDataInit(const uint8_t *snes,size_t snes_size,const uint8_t *md,size_t md_size);
int TlkRoarDataReady(void);
unsigned TlkRoarFireDelay(void);
int TlkRoarToken(unsigned index,unsigned *duration,unsigned *pose_or_target);
size_t TlkRoarDataRecordSize(void);
int TlkRoarDataWrite(uint8_t *data,size_t size);
int TlkRoarDataRead(const uint8_t *data,size_t size,int apply);
#endif
