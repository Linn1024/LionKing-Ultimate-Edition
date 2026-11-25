#ifndef TLK_MD_ASSETS_H
#define TLK_MD_ASSETS_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Input must be the verified MD World ROM. Data is decoded into owned buffers. */
int TlkMdAssetsInit(const uint8_t *rom, size_t size);
uint16_t TlkMdColor555(unsigned cram_word);
void TlkMdAssetsClear(void);
int TlkMdAssetsBindSnes(const uint8_t *rom, size_t size);
/* Local installation cache: source hashes and payload digest are mandatory.
 * Loading is transactional; corrupt/incompatible caches leave assets intact. */
int TlkMdAssetsLoadCache(const char *path,const uint8_t snes_hash[32],const uint8_t md_hash[32]);
int TlkMdAssetsSaveCache(const char *path,const uint8_t snes_hash[32],const uint8_t md_hash[32]);
uint16_t TlkMdSceneMappedPixel(unsigned level, unsigned native_cell, unsigned x, unsigned y);
/* Decode1..8 pixels within one8px tile. Returns1 only for a complete
 * supported run; otherwise keep the original scalar fallback. Tokens retain
 * transparency, palette, priority, flips and the current animation phase.
 * Background inputs are authored-plane coordinates, not a scroll recipe. */
int TlkMdSceneMappedPixels(unsigned level,unsigned native_cell,unsigned x,unsigned y,uint16_t *out,unsigned count);
int TlkMdSceneForegroundPixels(unsigned level,int x,int y,uint16_t *out,unsigned count);
int TlkMdSceneBackgroundPixels(unsigned level,int x,int y,uint16_t *out,unsigned count);
int TlkMdSceneCoverage(unsigned level, unsigned *matched, unsigned *total);
/* Cancel co-located copies, then pair only a unique remaining marker relocation. */
int TlkMdSceneMarkerMove(unsigned level,unsigned marker,int native_x,int native_y,int *md_x,int *md_y);
int TlkMdSceneMarkerDataReady(unsigned level);
int TlkMdSceneReady(unsigned snes_level);
/* Asset decoding does not prove that a scene's layer/scroll program is adapted. */
int TlkMdSceneBackgroundReady(unsigned snes_level);
/* Second-level immutable recipe, hydrated from the verified ROM after either
 * decoding or loading cache-v1. This does not enable its mixed scene adapter.
 * Palette words use original MD format; transition software owns 100 colors. */
int TlkMdCantWaitHydrate(const uint8_t *rom, size_t size);
int TlkMdCantWaitReady(void);
int TlkMdCantWaitInitialPalette(unsigned variant, uint16_t colors[64]);
int TlkMdCantWaitPaletteStep(uint16_t colors[100]);
unsigned TlkMdCantWaitLineOffset(unsigned camera_x, unsigned wrap_x, unsigned y);
/* Inputs belong to the completed original callback, not the following camera.
 * Returns a compositor token; no native palette/timing correspondence implied. */
uint16_t TlkMdCantWaitBackgroundPixel(unsigned camera_x, unsigned wrap_x, int x, int y);
int TlkMdSceneSize(unsigned snes_level, unsigned *width, unsigned *height);
/* Reskin selected MD foreground geometry with original native tile materials.
 * This is a visual adaptation, not proof of identical artwork in both ROMs. */
int TlkMdSceneNativeLayoutTile(unsigned level,int x,int y,const uint8_t *snes,
                             size_t size,uint16_t *word);
/* SNES-compositor token: priority<<12 | external-colour bit | layer<<8 | MD CRAM index. */
uint16_t TlkMdScenePixel(unsigned level, unsigned layer, int world_x, int world_y,
                       int camera_x, int camera_y, int screen_x, int screen_y,
                       int native_bg_x, int native_bg_y, int view_column, int view_width);
/* Verified background recipe, with the actual world-space left edge of the view. */
uint16_t TlkMdSceneBackgroundViewPixel(unsigned level,int view_left,int camera_y,int x,int y,int width);
/* Render cache only: the saved scene controller owns the animation clock.
 * Select before sampling either plane. Does not advance game or read ROM code. */
void TlkMdSceneAnimationPhase(unsigned level,unsigned phase);
/* Prepares palette mappings once per scanline, cached across identical lines. */
/* A scene owner may install its prepared normal animation colors. */
void TlkMdScenePreparedPalette(unsigned level,const uint16_t colors[64]);
void TlkMdScenePalette(unsigned level, const uint16_t *native_cgram, int md_palette);
/* Prepared original scene colors, independent of scenery source selection. */
int TlkMdScenePaletteColors(unsigned level, uint16_t colors[64]);
uint16_t TlkMdSceneColor(unsigned index, int external, uint16_t original);
uint16_t TlkMdSceneModeColor(unsigned index,int external,uint16_t original,int md);
/* Bounded decoder, also exercised against malformed streams by unit tests. */
int TlkMdDecompress(const uint8_t *rom, size_t size, size_t offset,
                    uint8_t *out, size_t capacity, size_t *written);
#ifdef __cplusplus
}
#endif
#endif
