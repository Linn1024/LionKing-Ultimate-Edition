#ifndef TLK_STATE_BYTES_H
#define TLK_STATE_BYTES_H
#include <stdint.h>
#include <string.h>
static inline uint32_t TlkGet32(const uint8_t *p) { return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24; }
static inline void TlkPut32(uint8_t *p,uint32_t v) { for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(i*8)); }
static inline uint64_t TlkGet64(const uint8_t *p) { return TlkGet32(p)|(uint64_t)TlkGet32(p+4)<<32; }
static inline void TlkPut64(uint8_t *p,uint64_t v) { TlkPut32(p,(uint32_t)v);TlkPut32(p+4,(uint32_t)(v>>32)); }
static inline double TlkGetDouble(const uint8_t *p) { uint64_t v=TlkGet64(p);double d;memcpy(&d,&v,8);return d; }
static inline void TlkPutDouble(uint8_t *p,double d) { uint64_t v;memcpy(&v,&d,8);TlkPut64(p,v); }
#endif
