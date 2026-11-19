#include "tlk_final_native_internal.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>

static const TlkFinalNativeRecipe recipes[TLK_FINAL_NATIVE_COUNT]={
    {0xd545ec,0x7f0000,0,0x7f8b80,35712},
    {0xee6e03,0x7e4434,0xee756d,0x7e7450,12316},
    {0xe922ed,0x7f0000,0xe93440,0x7f186a,6250},
    {0xd34ccb,0x7f0000,0xd398c5,0x7f7b40,31552},
    {0xc9f9e1,0x7e2434,0xc9ffe7,0x7e3ab4,5760},
    {0xe20001,0x7f0000,0xe22292,0x7f3e80,16000},
    {0xe7c514,0x7f8800,0xe7d9e7,0x7faf80,10112},
    {0xe8c1a3,0x7fba00,0xe8d405,0x7fd780,7552},
    {0xefe261,0x7fd780,0xefe3cd,0x7fe000,2176},
    {0xecf6c1,0x7fe000,0xecfff3,0x7fef00,3840},
    {0xed8d99,0x7f0000,0xed969d,0x7f12ce,4814},
    {0xdb0001,0x7f0000,0xdb32c5,0x7f4ac0,19136},
    {0xefc646,0x7f0000,0xefc8e0,0x7f0800,2048},
    {0xefb50c,0x7f0800,0xefb81f,0x7f1000,2048},
    {0xd64371,0x7f0000,0xd685d9,0x7f5b40,23360},
    {0xed0001,0x7f8800,0xed0a02,0x7f9800,4096},
    {0xef7073,0x7e7ae4,0xef74a6,0x7e80e4,1536},
    {0xefcb64,0x7f0000,0xefcdcd,0x7f0700,1792},
    {0xef67cd,0x7f0800,0xef6c29,0x7f0f00,1792},
    {0xe94540,0x7f0000,0xe95637,0x7f2080,8320},
};
struct TlkFinalNative { uint8_t *bytes;size_t offset[TLK_FINAL_NATIVE_COUNT]; };
static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
const TlkFinalNativeRecipe *TlkFinalNativeRecipeAt(unsigned index) {
    return index<TLK_FINAL_NATIVE_COUNT?recipes+index:NULL;
}
void TlkFinalNativeFree(TlkFinalNative *assets) {
    if(assets){free(assets->bytes);free(assets);}
}
TlkFinalNative *TlkFinalNativeLoad(const uint8_t *data,size_t size) {
    if(!data || size<112 || size>1024*1024 || memcmp(data,"TLKFNAT1",8) ||
       get32(data+8)!=2 || get32(data+12)!=112 || get32(data+16)!=size ||
       get32(data+20)!=TLK_FINAL_NATIVE_COUNT || memcmp(data+24,tlk_final_native_source,32))return NULL;
    for(unsigned i=88;i<112;i++)if(data[i])return NULL;
    uint8_t hash[32];sha256_compute(data+112,size-112,hash);if(memcmp(hash,data+56,32))return NULL;
    TlkFinalNative *assets=calloc(1,sizeof *assets);if(!assets)return NULL;
    size_t pos=112;
    for(unsigned i=0;i<TLK_FINAL_NATIVE_COUNT;i++) {
        const TlkFinalNativeRecipe *r=recipes+i;
        if(size-pos<20 || get32(data+pos)!=r->source || get32(data+pos+4)!=r->destination ||
           get32(data+pos+8)!=r->source_end || get32(data+pos+12)!=r->destination_end ||
           get32(data+pos+16)!=r->size)goto fail;
        pos+=20;if(r->size>size-pos)goto fail;assets->offset[i]=pos;pos+=r->size;
    }
    if(pos!=size)goto fail;
    assets->bytes=malloc(size);if(!assets->bytes)goto fail;
    memcpy(assets->bytes,data,size);return assets;
fail:
    TlkFinalNativeFree(assets);return NULL;
}
const uint8_t *TlkFinalNativePayload(const TlkFinalNative *assets,unsigned index,size_t *size) {
    if(size)*size=0;
    if(!assets || index>=TLK_FINAL_NATIVE_COUNT)return NULL;
    if(size)*size=recipes[index].size;return assets->bytes+assets->offset[index];
}
