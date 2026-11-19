#ifndef TLK_TITLE_ART_H
#define TLK_TITLE_ART_H
#include <stddef.h>
#include <stdint.h>
typedef struct TlkTitleArt TlkTitleArt;
/* Independently decoded/owned Pride captions. Full ROM identities checked.
 * No live guest/ROM pointers retained. Coordinates: caption centre / line top. */
TlkTitleArt *TlkTitleArtCreate(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms);
/* Prepared caption playback; malformed/missing data returns NULL, no ROM decode. */
TlkTitleArt *TlkTitleArtLoad(const uint8_t *record,size_t size);
TlkTitleArt *TlkTitleArtReadFile(const char *path);
/* Installer-only entry; validates both ROMs through the original decoder. */
int TlkTitleArtPrepare(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms,
                       uint8_t **record,size_t *size);
void TlkTitleArtFree(TlkTitleArt *art);
int TlkTitleArtBounds(const TlkTitleArt *art,unsigned source,int *x,int *y,int *w,int *h);
/* -1 requests untouched native fallback,0 transparent,1 opaque RGB555.
 * Caller owns scene, task, OAM, position and lifetime validation. */
int TlkTitleArtSample(const TlkTitleArt *art,int x,int y,unsigned frames,unsigned palette,
                      const uint16_t cgram[256],uint16_t *color);
/* Remaining level captions plus the separate King instruction. Slots1..15
 * identify exact prepared native text packets;0 is unavailable/unmatched. */
int TlkTitleArtCaptionsReady(const TlkTitleArt *art);
unsigned TlkTitleArtCaptionMatch(const TlkTitleArt *art,unsigned level,unsigned hint,
                                const uint8_t *packet,size_t size);
int TlkTitleArtCaptionBounds(const TlkTitleArt *art,unsigned slot,int *x,int *y,int *w,int *h);
int TlkTitleArtCaptionSample(const TlkTitleArt *art,unsigned slot,int x,int y,unsigned palette,
                            const uint16_t *native,const uint16_t *cgram,uint16_t *color);
int TlkTitleArtCaptionColor(const TlkTitleArt *art,unsigned slot,unsigned pixel,
                           const uint16_t *native,const uint16_t *cgram,uint16_t *color);
#endif
