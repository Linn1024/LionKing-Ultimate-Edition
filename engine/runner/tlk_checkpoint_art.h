#ifndef TLK_CHECKPOINT_ART_H
#define TLK_CHECKPOINT_ART_H
#include <stddef.h>
#include <stdint.h>

typedef struct TlkCheckpointArt TlkCheckpointArt;
/* Owns the independently decoded original head images and palettes. Full ROM
 * identities are checked; no source ROM or guest pointer is retained. */
TlkCheckpointArt *TlkCheckpointArtCreate(const uint8_t *snes,size_t snes_size,
                                        const uint8_t *md,size_t md_size);
TlkCheckpointArt *TlkCheckpointArtLoad(const uint8_t *record,size_t size);
TlkCheckpointArt *TlkCheckpointArtReadFile(const char *path);
/* Installer-only entry. Original source decoder verifies equal source pixels. */
int TlkCheckpointArtPrepare(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms,
                            uint8_t **record,size_t *size);
void TlkCheckpointArtFree(TlkCheckpointArt *art);
int TlkCheckpointArtBounds(const TlkCheckpointArt *art,int *x,int *y,int *w,int *h);
int TlkCheckpointArtPixel(const TlkCheckpointArt *art,int x,int y,unsigned source);
int TlkCheckpointArtPoseBounds(const TlkCheckpointArt *art,uint32_t pose,int *x,int *y,int *w,int *h);
int TlkCheckpointArtPosePixel(const TlkCheckpointArt *art,uint32_t pose,int x,int y,unsigned source);
int TlkCheckpointArtPoseSample(const TlkCheckpointArt *art,uint32_t pose,int x,int y,
                              unsigned frames,unsigned palette,const uint16_t cgram[256],uint16_t *color);
/* Independent image/palette sources:0 native,1 MD. Returns -1 for native
 * fallback,0 transparent,1 opaque RGB555. Rejection/transparency leave color
 * unchanged. The caller must validate semantic task identity, scene ownership,
 * physical OAM, palette bank0, placement, priority and fade timing separately.
 * A repurposed/flash native palette is rejected rather than recolored. */
int TlkCheckpointArtSample(const TlkCheckpointArt *art,int x,int y,
                          unsigned frames,unsigned palette,
                          const uint16_t cgram[256],uint16_t *color);
#endif
