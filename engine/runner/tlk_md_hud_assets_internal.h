#ifndef TLK_MD_HUD_ASSETS_INTERNAL_H
#define TLK_MD_HUD_ASSETS_INTERNAL_H
#include "tlk_md_hud_assets.h"
#include "sha256.h"
#include <string.h>
enum { TLK_HUD_HEADER=112, TLK_HUD_START=0x8ec14, TLK_HUD_END=0x8fdc6 };
static const uint8_t tlk_hud_md_source[32]={
    0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,
    0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
static uint32_t hud_u32(const uint8_t *p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void hud_put32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(i*8));}
static int hud_record_valid(const uint8_t *p,size_t size){
    if(!p || size!=TLK_HUD_HEADER+TLK_MD_HUD_PAYLOAD_BYTES || memcmp(p,"TLKHUD01",8) ||
       hud_u32(p+8)!=1 || hud_u32(p+12)!=TLK_MD_HUD_PAYLOAD_BYTES ||
       memcmp(p+16,tlk_hud_md_source,32) || hud_u32(p+48)!=TLK_HUD_START ||
       hud_u32(p+52)!=TLK_HUD_END || hud_u32(p+56)!=0x01020304)return 0;
    for(unsigned i=60;i<80;i++)if(p[i])return 0;
    uint8_t digest[32];sha256_compute(p+TLK_HUD_HEADER,TLK_MD_HUD_PAYLOAD_BYTES,digest);
    return !memcmp(p+80,digest,32);
}
#endif
