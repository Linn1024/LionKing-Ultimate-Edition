#ifndef TLK_FINAL_NATIVE_PREPARE_H
#define TLK_FINAL_NATIVE_PREPARE_H
#include <stddef.h>
#include <stdint.h>
/* Installer only. Verified SNES USA input; caller frees the output record. */
int TlkFinalNativePrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size);
#endif
