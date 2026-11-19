#ifndef TLK_DATA_RECORD_H
#define TLK_DATA_RECORD_H
#include <stdint.h>
static inline uint32_t TlkDataGet32(const uint8_t *p) {return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static inline void TlkDataPut32(uint8_t *p,uint32_t value) {for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(value>>(8*i));}
static inline uint16_t TlkDataGet16(const uint8_t *p) {return (uint16_t)(p[0]|(unsigned)p[1]<<8);}
static inline void TlkDataPut16(uint8_t *p,unsigned value) {p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);}
#endif
