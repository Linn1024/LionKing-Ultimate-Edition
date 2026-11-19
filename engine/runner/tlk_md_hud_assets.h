#ifndef TLK_MD_HUD_ASSETS_H
#define TLK_MD_HUD_ASSETS_H
#include <stddef.h>
#include <stdint.h>
enum { TLK_MD_HUD_PAYLOAD_BYTES=0x8fdc6-0x8ec14 };
/* Invalid records leave the previously installed immutable payload intact. */
int TlkMdHudAssetsLoad(const uint8_t *record,size_t size);
int TlkMdHudAssetsReadFile(const char *path);
int TlkMdHudAssetsReady(void);
int TlkMdHudAssetsActivate(void);
/* Internal bridge into the unchanged dynamic meter/portrait renderer. */
int TlkMdHudInitPrepared(const uint8_t *payload,size_t size);
#endif
