#ifndef TLK_TITLE_BANK_PREPARE_H
#define TLK_TITLE_BANK_PREPARE_H
#include <stddef.h>
#include <stdint.h>
/* Installer-only source decoding; playback links only the separate reader. */
int TlkTitleBankPrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size);
#endif
