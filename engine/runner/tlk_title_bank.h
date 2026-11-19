#ifndef TLK_TITLE_BANK_H
#define TLK_TITLE_BANK_H
#include <stddef.h>
#include <stdint.h>

enum { TLK_TITLE_BANK_PACKETS=16, TLK_TITLE_BANK_ID=5,
       TLK_TITLE_BANK_BASE=0x25c8, TLK_TITLE_BANK_SCORE=0x25f9,
       TLK_TITLE_BANK_END=0xf4fb };
typedef struct TlkTitleBank TlkTitleBank;
typedef struct TlkTitleBankPacket {
    uint32_t source,destination,size,command,id,directory;
} TlkTitleBankPacket;
/* Original bank5 queue program: common effects(3), score(1),14 samples(2).
 * This package contains source packets and destinations, not a chip snapshot.
 * Reading it alone does not implement the SPC transfer/driver state changes. */
const TlkTitleBankPacket *TlkTitleBankPacketAt(unsigned index);
TlkTitleBank *TlkTitleBankLoad(const uint8_t *record,size_t size);
void TlkTitleBankFree(TlkTitleBank *bank);
const uint8_t *TlkTitleBankPayload(const TlkTitleBank *bank,unsigned index,size_t *size);
#endif
