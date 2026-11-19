#ifndef TLK_PRIDE_DATA_H
#define TLK_PRIDE_DATA_H
#include <stddef.h>
#include <stdint.h>
/* Immutable supported-source tables bundled with installed sprite assets. */
int TlkPrideDataPrepare(const uint8_t *snes,size_t snes_size,const uint8_t *md,size_t md_size);
size_t TlkPrideDataRecordSize(void);
int TlkPrideDataWrite(uint8_t *data,size_t size);
int TlkPrideDataRead(const uint8_t *data,size_t size,int apply);
#endif
