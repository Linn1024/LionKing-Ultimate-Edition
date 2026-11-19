#include "tlk_title_bank.h"
#include "tlk_final_native_internal.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>

static const TlkTitleBankPacket packets[TLK_TITLE_BANK_PACKETS]={
    {0xefe67b,0x25c8,336,3,0,0},
    {0xed8d99,0x25f9,4814,1,0,0},
    {0xefa412,0x38c7,900,2,1,0x2304},
    {0xef0b2d,0x3c4b,1394,2,63,0x23fc},
    {0xeecdb0,0x41bd,1602,2,16,0x2340},
    {0xe8aeef,0x47ff,4788,2,82,0x2448},
    {0xed7253,0x5ab3,2330,2,41,0x23a4},
    {0xef109f,0x63cd,1386,2,30,0x2378},
    {0xde2c01,0x6937,11250,2,17,0x2344},
    {0xe2eac9,0x9529,5372,2,74,0x2428},
    {0xe51a01,0xaa25,6650,2,22,0x2358},
    {0xe473e9,0xc41f,7002,2,23,0x235c},
    {0xee925e,0xdf79,1782,2,0,0x2300},
    {0xeeba9c,0xe66f,1628,2,25,0x2364},
    {0xef9ce5,0xeccb,936,2,26,0x2368},
    {0xef5a69,0xf073,1160,2,50,0x23c8},
};
struct TlkTitleBank { uint8_t *bytes;size_t offsets[TLK_TITLE_BANK_PACKETS]; };
static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
const TlkTitleBankPacket *TlkTitleBankPacketAt(unsigned index) {
    return index<TLK_TITLE_BANK_PACKETS?packets+index:NULL;
}
void TlkTitleBankFree(TlkTitleBank *bank) {if(bank){free(bank->bytes);free(bank);}}
TlkTitleBank *TlkTitleBankLoad(const uint8_t *data,size_t size) {
    if(!data || size<112 || size>1024*1024 || memcmp(data,"TLKTBK01",8) ||
       get32(data+8)!=1 || get32(data+12)!=112 || get32(data+16)!=size ||
       get32(data+20)!=TLK_TITLE_BANK_PACKETS || memcmp(data+24,tlk_final_native_source,32) ||
       get32(data+88)!=TLK_TITLE_BANK_ID || get32(data+92)!=TLK_TITLE_BANK_BASE ||
       get32(data+96)!=TLK_TITLE_BANK_SCORE || get32(data+100)!=TLK_TITLE_BANK_END)return NULL;
    for(unsigned i=104;i<112;i++)if(data[i])return NULL;
    uint8_t hash[32];sha256_compute(data+112,size-112,hash);if(memcmp(hash,data+56,32))return NULL;
    TlkTitleBank *bank=calloc(1,sizeof *bank);if(!bank)return NULL;
    size_t pos=112;
    for(unsigned i=0;i<TLK_TITLE_BANK_PACKETS;i++) {
        const TlkTitleBankPacket *p=packets+i;
        if(size-pos<24 || get32(data+pos)!=p->source || get32(data+pos+4)!=p->destination ||
           get32(data+pos+8)!=p->size || get32(data+pos+12)!=p->command ||
           get32(data+pos+16)!=p->id || get32(data+pos+20)!=p->directory)goto fail;
        pos+=24;if(p->size>size-pos)goto fail;bank->offsets[i]=pos;pos+=p->size;
    }
    if(pos!=size)goto fail;
    bank->bytes=malloc(size);if(!bank->bytes)goto fail;memcpy(bank->bytes,data,size);return bank;
fail:
    TlkTitleBankFree(bank);return NULL;
}
const uint8_t *TlkTitleBankPayload(const TlkTitleBank *bank,unsigned index,size_t *size) {
    if(size)*size=0;
    if(!bank || index>=TLK_TITLE_BANK_PACKETS)return NULL;
    if(size)*size=packets[index].size;return bank->bytes+bank->offsets[index];
}
