#ifndef TLK_CW_TERRAIN_DATA_H
#define TLK_CW_TERRAIN_DATA_H
#include <stddef.h>
#include <stdint.h>
void TlkCwTerrainDataClear(void);
int TlkCwTerrainDataPrepare(const uint8_t *,size_t,const uint8_t *,size_t);
size_t TlkCwTerrainDataSize(void);
int TlkCwTerrainDataWrite(uint8_t *,size_t);
int TlkCwTerrainDataRead(const uint8_t *,size_t,int apply);
int TlkCwTerrainDataPoint(unsigned cell,unsigned live,unsigned native_column,unsigned md_column,unsigned native,unsigned *external);
/*kind0: contact attribute; kind1: raw floor profile byte. */
int TlkCwTerrainDataGet(unsigned cell,unsigned live,unsigned kind,unsigned column,unsigned native,unsigned *external);
#endif
