#ifndef TLK_MD_SPRITE_ASSETS_H
#define TLK_MD_SPRITE_ASSETS_H
#include <stddef.h>
#include <stdint.h>
int TlkMdSpriteAssetsLoad(const uint8_t *record,size_t size);
int TlkMdSpriteAssetsReadFile(const char *path);
int TlkMdSpriteAssetsReady(void);
int TlkMdSpriteAssetsActivate(void);
int TlkMdSpriteAssetsSharedPalettes(uint16_t *native,uint16_t *md);
#endif
