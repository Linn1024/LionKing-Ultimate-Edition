/* Installation-only extraction from the verified complete MD source. */
#include "tlk_md_hud_prepare.h"
#include "tlk_md_hud_assets_internal.h"
#include <stdlib.h>
int TlkMdHudPrepareAssets(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size){
    if(record)*record=NULL;if(record_size)*record_size=0;
    if(!rom || size!=0x300000 || !record || !record_size)return 0;
    uint8_t hash[32];sha256_compute(rom,size,hash);if(memcmp(hash,tlk_hud_md_source,32))return 0;
    size_t total=TLK_HUD_HEADER+TLK_MD_HUD_PAYLOAD_BYTES;
    uint8_t *p=calloc(1,total);if(!p)return 0;
    memcpy(p,"TLKHUD01",8);hud_put32(p+8,1);hud_put32(p+12,TLK_MD_HUD_PAYLOAD_BYTES);
    memcpy(p+16,hash,32);hud_put32(p+48,TLK_HUD_START);hud_put32(p+52,TLK_HUD_END);hud_put32(p+56,0x01020304);
    memcpy(p+TLK_HUD_HEADER,rom+TLK_HUD_START,TLK_MD_HUD_PAYLOAD_BYTES);
    sha256_compute(p+TLK_HUD_HEADER,TLK_MD_HUD_PAYLOAD_BYTES,p+80);
    if(!hud_record_valid(p,total)){free(p);return 0;}
    *record=p;*record_size=total;return 1;
}
