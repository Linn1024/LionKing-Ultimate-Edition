#ifndef TLK_REACTIVATION_DATA_H
#define TLK_REACTIVATION_DATA_H
#include <stddef.h>
#include <stdint.h>
void TlkReactivationDataClear(void);
int TlkReactivationDataInit(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn);
int TlkReactivationDataFlags(unsigned *native,unsigned *external);
size_t TlkReactivationDataRecordSize(void);
int TlkReactivationDataWrite(uint8_t *data,size_t size);
int TlkReactivationDataRead(const uint8_t *data,size_t size,int apply);
#endif
