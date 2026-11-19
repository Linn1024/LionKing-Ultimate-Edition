#ifndef TLK_REVIVAL_ART_H
#define TLK_REVIVAL_ART_H
#include <stddef.h>
#include <stdint.h>
typedef struct TlkRevivalArt TlkRevivalArt;
/* Complete, independently decoded SNES/MD checkpoint revival and idle images.
 * Both full ROM identities and the original animation streams are checked.
 * Owns all pixels; no ROM or live WRAM pointer is retained. NULL on failure. */
TlkRevivalArt *TlkRevivalArtCreate(const uint8_t *snes,size_t snes_size,const uint8_t *md,size_t md_size);
/* Three checkpoint images (base and two collection poses), independently
 * decoded and owned. Does not assert original animation timing or ownership. */
TlkRevivalArt *TlkRevivalArtCreateCheckpoint(const uint8_t *snes,size_t snes_size,const uint8_t *md,size_t md_size);
/* Pride caption: original native ROM letters and the original prebuilt MD
 * picture. Coordinates are relative to caption centre X / first-line top Y.
 * These images intentionally differ; no timing or scene ownership is implied. */
TlkRevivalArt *TlkRevivalArtCreatePrideTitle(const uint8_t *snes,size_t snes_size,const uint8_t *md,size_t md_size);
/* Installer-only complete MD caption decode, relative to160/72. */
int TlkRevivalArtDecodeMdCaption(const uint8_t *md,size_t size,unsigned frame,int geometry[4],uint8_t **pixels);
/* Installed revival images; no ROM decode. Clone owns an independent copy. */
TlkRevivalArt *TlkRevivalArtLoad(const uint8_t *record,size_t size);
TlkRevivalArt *TlkRevivalArtReadFile(const char *path);
TlkRevivalArt *TlkRevivalArtClone(const TlkRevivalArt *art);
/* Installer-only, with TLK_REVIVAL_ART_PREPARE. */
int TlkRevivalArtPrepare(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms,
                         uint8_t **record,size_t *size);
void TlkRevivalArtFree(TlkRevivalArt *art);
unsigned TlkRevivalArtCount(const TlkRevivalArt *art);
int TlkRevivalArtBounds(const TlkRevivalArt *art,uint32_t snes_pose,int *x,int *y,int *w,int *h);
int TlkRevivalArtSourceBounds(const TlkRevivalArt *art,uint32_t pose,unsigned source,int *x,int *y,int *w,int *h);
/* Pose-local coordinates, same origin for the independently checked pair.
 * source: 0 SNES, 1 MD. Returns 0 transparent, 1..15 index, -1 unavailable.
 * Scene ownership, position, flips and palette remain the caller's job. */
int TlkRevivalArtPixel(const TlkRevivalArt *art,uint32_t snes_pose,int x,int y,unsigned source);
#endif
