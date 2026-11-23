/* Version choices belong to semantic resources, never to console addresses. */
#ifndef TLK_RESOURCES_H
#define TLK_RESOURCES_H
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#ifdef __cplusplus
extern "C" {
#endif

enum { TLK_SOURCE_INHERIT, TLK_SOURCE_SNES, TLK_SOURCE_MD };
enum { TLK_CHANGE_LIVE, TLK_CHANGE_LEVEL, TLK_CHANGE_GAME };
typedef struct TlkResourceNode {
    const char *id, *label;
    int parent, leaf, change, md_supported;
    const char *scope;
} TlkResourceNode;

/* Custom colours are per level and foreground/background/objects, independent of source. */
int TlkResourcesPaletteCount(int draft);
int TlkResourcesPaletteEntry(int index,int draft,int out[4]);
int TlkResourcesPaletteSet(int level,int layer,int from,int to);
void TlkResourcesPaletteReset(int level,int layer);
void TlkResourcesPalettePreview(int on);
uint16_t TlkResourcesPaletteMap(unsigned level,unsigned layer,uint16_t color);
/* Independent sprite colours, across levels and separated by palette source. */
int TlkResourcesSpritePaletteNode(int node);
uint16_t TlkResourcesSpritePaletteMap(int node,int md,uint16_t color);
int TlkResourcesPaletteDecode(const char *id,const char *value,int out[4]);
int TlkResourcesPaletteEncode(const int entry[4],char *out,size_t size);
void TlkResourcesInit(const uint8_t *snes, size_t size, const char *md_path, const char *profile);
void TlkResourcesSetCachePath(const char *path,int prepare);
void TlkResourcesSetTitleAssetsPath(const char *path);
int TlkResourcesTitleAssetsReady(void);
void TlkResourcesSetCheckpointAssetsPath(const char *path);
int TlkResourcesCheckpointAssetsReady(void);
void TlkResourcesSetRevivalAssetsPath(const char *path);
int TlkResourcesRevivalAssetsReady(void);
struct TlkRevivalArt *TlkResourcesRevivalArtCopy(void);
void TlkResourcesSetNativeHudAssetsPath(const char *path);
int TlkResourcesNativeHudAssetsReady(void);
struct TlkNativeHud *TlkResourcesNativeHudCopy(void);
int TlkResourcesCachePrepared(void);
int TlkResourcesCount(void);
const TlkResourceNode *TlkResourcesNode(int index);
int TlkResourcesFind(const char *id);
int TlkResourcesChoice(int index, int draft);
int TlkResourcesResolved(int index, int draft);
/* Paused renderer only: compare a graphics branch using draft artwork without
 * applying/persisting choices or changing gameplay/audio resolution. */
void TlkResourcesPreviewBegin(int index,int source);
void TlkResourcesPreviewEnd(void);
int TlkResourcesSet(int index, int source);
int TlkResourcesDirty(void);
void TlkResourcesRevert(void);
void TlkResourcesDefaults(void);
void TlkResourcesGraphicsPreset(void);
/* Draft only: select every currently available MD leaf, leave others SNES. */
void TlkResourcesMdPreset(void);
int TlkResourcesValidate(char *reason, size_t size);
/* Validate and persist first; activate only if both succeed. 0 on failure. */
int TlkResourcesApply(void);
const char *TlkResourcesStatus(void);
const char *TlkResourcesMdStatus(void);
int TlkResourcesMixed(void);
int TlkResourcesViewportWidth(void);
/* Native MD H32 exception; explicit widescreen overrides remain host choices. */
int TlkResourcesViewportForScene(unsigned level);
int TlkResourcesPresentation(void);
int TlkResourcesHasMd(void);
int TlkResourcesUseMd(const char *id);
/* Diagnostic policy: every supported leaf below this group is selected MD. */
static inline int TlkResourcesGroupMd(const char *prefix) {
    size_t len=prefix?strlen(prefix):0;int found=0;
    if(!len)return 0;
    for(int i=0;i<TlkResourcesCount();i++) {
        const TlkResourceNode *n=TlkResourcesNode(i);
        if(n && n->leaf && n->md_supported && !strncmp(n->id,prefix,len) &&
           (!n->id[len] || n->id[len]=='.')) {
            found=1;if(!TlkResourcesUseMd(n->id))return 0;
        }
    }
    return found;
}
/* Artwork source: roar=0, health=1, lives=2; inherited from Meters and lives. */
int TlkResourcesHudFramesMd(unsigned kind);
/* The host compositor calls this for a tagged Simba OBJ pixel. Cub and adult
 * choices are independent; unmatched/flash palettes retain the original. */
uint16_t TlkResourcesCubColor(unsigned level, unsigned palette_index,
                              const uint16_t *cgram, uint16_t original);
uint16_t TlkResourcesHudColor(unsigned palette_index,const uint16_t *cgram,uint16_t original);
int TlkResourcesSharedPaletteMatches(const uint16_t *cgram);
/* Shared indexed artwork: caller verifies the object and its own source choice.
 * Preserves an unmatched native palette; independent of Simba/HUD choices. */
uint16_t TlkResourcesSharedObjColor(unsigned index,const uint16_t *cgram,uint16_t original);
/* Caller establishes checkpoint semantic/physical ownership and palette bank0. */
int TlkResourcesCheckpointSample(uint32_t pose,int x,int y,unsigned frames,unsigned palette,
                                  const uint16_t *cgram,uint16_t *color);
int TlkResourcesTitleBounds(unsigned source,int *x,int *y,int *w,int *h);
int TlkResourcesTitleSample(int x,int y,unsigned frames,unsigned palette,const uint16_t *cgram,uint16_t *color);
unsigned TlkResourcesCaptionMatch(unsigned level,unsigned hint,const uint8_t *packet,size_t size);
int TlkResourcesCaptionBounds(unsigned slot,int *x,int *y,int *w,int *h);
int TlkResourcesCaptionSample(unsigned slot,int x,int y,unsigned palette,const uint16_t *cgram,uint16_t *color);
int TlkResourcesCaptionColor(unsigned slot,unsigned pixel,const uint16_t *cgram,uint16_t *color);
#ifdef __cplusplus
}
#endif
#endif
