#include "tlk_final_native_internal.h"
#include "tlk_final_native_prepare.h"
#include "tlk_md_assets.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>

static void put32(uint8_t *p,uint32_t value) {
    for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(value>>(i*8));
}
int TlkFinalNativePrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size) {
    if(record)*record=NULL;if(record_size)*record_size=0;
    if(!record || !record_size || !rom || size!=0x300000)return 0;
    uint8_t hash[32];sha256_compute(rom,size,hash);if(memcmp(hash,tlk_final_native_source,32))return 0;
    size_t total=112;
    for(unsigned i=0;i<TLK_FINAL_NATIVE_COUNT;i++)total+=20+TlkFinalNativeRecipeAt(i)->size;
    uint8_t *data=calloc(1,total);if(!data)return 0;
    memcpy(data,"TLKFNAT1",8);put32(data+8,2);put32(data+12,112);put32(data+16,(uint32_t)total);
    put32(data+20,TLK_FINAL_NATIVE_COUNT);memcpy(data+24,hash,32);size_t pos=112;
    for(unsigned i=0;i<TLK_FINAL_NATIVE_COUNT;i++) {
        const TlkFinalNativeRecipe *r=TlkFinalNativeRecipeAt(i);
        put32(data+pos,r->source);put32(data+pos+4,r->destination);put32(data+pos+8,r->source_end);
        put32(data+pos+12,r->destination_end);put32(data+pos+16,r->size);pos+=20;
        size_t written=0;
        if(!TlkMdDecompress(rom,size,r->source&0x3fffff,data+pos,r->size,&written) || written!=r->size) {
            free(data);return 0;
        }
        pos+=written;
    }
    sha256_compute(data+112,total-112,data+56);*record=data;*record_size=total;return 1;
}
