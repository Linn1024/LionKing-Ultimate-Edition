#include "tlk_title_bank.h"
#include "tlk_title_bank_prepare.h"
#include "tlk_final_native_internal.h"
#include "tlk_md_assets.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>

static void put32(uint8_t *p,uint32_t value) {for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(value>>(i*8));}
int TlkTitleBankPrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size) {
    if(record)*record=NULL;if(record_size)*record_size=0;
    if(!record || !record_size || !rom || size!=0x300000)return 0;
    uint8_t hash[32];sha256_compute(rom,size,hash);if(memcmp(hash,tlk_final_native_source,32))return 0;
    size_t total=112;
    for(unsigned i=0;i<TLK_TITLE_BANK_PACKETS;i++)total+=24+TlkTitleBankPacketAt(i)->size;
    uint8_t *data=calloc(1,total);if(!data)return 0;
    memcpy(data,"TLKTBK01",8);put32(data+8,1);put32(data+12,112);put32(data+16,(uint32_t)total);
    put32(data+20,TLK_TITLE_BANK_PACKETS);memcpy(data+24,hash,32);
    put32(data+88,TLK_TITLE_BANK_ID);put32(data+92,TLK_TITLE_BANK_BASE);
    put32(data+96,TLK_TITLE_BANK_SCORE);put32(data+100,TLK_TITLE_BANK_END);
    size_t pos=112;
    for(unsigned i=0;i<TLK_TITLE_BANK_PACKETS;i++) {
        const TlkTitleBankPacket *p=TlkTitleBankPacketAt(i);
        put32(data+pos,p->source);put32(data+pos+4,p->destination);put32(data+pos+8,p->size);
        put32(data+pos+12,p->command);put32(data+pos+16,p->id);put32(data+pos+20,p->directory);pos+=24;
        unsigned source=p->source&0x3fffff;
        if(p->command==1) {
            size_t written=0;
            if(!TlkMdDecompress(rom,size,source,data+pos,p->size,&written) || written!=p->size)goto fail;
        } else {
            if(source>size || p->size>size-source || (rom[source]|(unsigned)rom[source+1]<<8)!=p->size)goto fail;
            if(p->command==2 && (rom[source+2]!=1 || rom[source+3]!=p->id))goto fail;
            memcpy(data+pos,rom+source,p->size);
        }
        pos+=p->size;
    }
    sha256_compute(data+112,total-112,data+56);*record=data;*record_size=total;return 1;
fail:
    free(data);return 0;
}
