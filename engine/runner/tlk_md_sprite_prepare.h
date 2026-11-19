#ifndef TLK_MD_SPRITE_PREPARE_H
#define TLK_MD_SPRITE_PREPARE_H
#include <stddef.h>
#include <stdint.h>
int TlkMdSpriteAssetsPrepare(const uint8_t *snes,size_t snes_size,const uint8_t *md,size_t md_size,
                            uint8_t **record,size_t *record_size);
#endif
