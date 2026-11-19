#ifndef TLK_MD_SPRITES_H
#define TLK_MD_SPRITES_H
#include <stdint.h>
#include <stddef.h>
enum { TLK_MD_SPRITE_NONE, TLK_MD_SPRITE_HYENA, TLK_MD_SPRITE_LIZARD,
       TLK_MD_SPRITE_PORCUPINE, TLK_MD_SPRITE_PICKUP, TLK_MD_SPRITE_LEAVES,
       TLK_MD_SPRITE_DEFEAT_PUFF,
       TLK_MD_SPRITE_PICKUP_POPUP,
       TLK_MD_SPRITE_CONTINUE_TOKEN,
       TLK_MD_SPRITE_CW_RHINO,
       TLK_MD_SPRITE_GRAVEYARD_VULTURE,
       TLK_MD_SPRITE_STAMPEDE_CUB, TLK_MD_SPRITE_STAMPEDE_ROCK,
       TLK_MD_SPRITE_GORILLA,
       TLK_MD_SPRITE_LATER_ENEMY, TLK_MD_SPRITE_LATER_WORLD,
       TLK_MD_SPRITE_LATER_EFFECT, TLK_MD_SPRITE_LATER_PICKUP,
       TLK_MD_SPRITE_DESTINY_MONKEY,
       TLK_MD_SPRITE_ADULT_HYENA, TLK_MD_SPRITE_SCAR,
       TLK_MD_SPRITE_BONUS_PUMBAA, TLK_MD_SPRITE_BONUS_TIMON, TLK_MD_SPRITE_BONUS_BUG,
       TLK_MD_SPRITE_CW_HIPPO,
       TLK_MD_SPRITE_COCONUT,
       TLK_MD_SPRITE_CW_RIDE_OBSTACLE,
       TLK_MD_SPRITE_CW_GIRAFFE,
       TLK_MD_SPRITE_GRAVEYARD_BONE_OBJECT,
       TLK_MD_SPRITE_GRAVEYARD_PILLAR,
       TLK_MD_SPRITE_ROLE_COUNT };
/* Scene ownership only; unknown individual poses still use native art. */
int TlkMdSpritesCubScene(unsigned level,unsigned descriptor);
/* Current prepared second-level CRAM colors, refreshed by the scene renderer. */
void TlkMdSpritesCantWaitPalette(const uint16_t colors[64]);
/* Prepared BGR555 scene colors; NULL restores the original Pride palette path. */
void TlkMdSpritesGraveyardPalette(const uint16_t colors[64]);
/* Scene palettes are installed data; zero restores the original NPC paths. */
void TlkMdSpritesNextScene(unsigned level);
/* Scene-owned death graphics must match the native loader's decoded bank. */
int TlkMdSpritesCubDeathReady(unsigned pose,const uint8_t *wram,size_t size);
int TlkMdSpritesCubDeathPose(unsigned pose);
/* Private ROM-owned art, available before the live death bank is loaded.
 * Count is20 only when the complete native set is decoded and verified.
 * Pixels use pose-local coordinates; -1 requests native fallback,0 is clear.
 * Scene ownership remains the caller's responsibility. */
unsigned TlkMdSpritesCubDeathAssetCount(void);
int TlkMdSpritesCubDeathPixel(unsigned pose,int x,int y,int md_frames);
int TlkMdSpritesInit(const uint8_t *rom,size_t size);
void TlkMdSpritesClear(void);
int TlkMdSpritesPixel(unsigned pose,int x,int y);
void TlkMdSpritesBindSnes(const uint8_t *rom,size_t size);
/* Semantic role; zero means no first-level adapter. */
unsigned TlkMdSpritesRole(unsigned pose);
/* Diagnostic lookup never marks art as seen or changes sampler decisions. */
int TlkMdSpritesDescribe(unsigned pose,unsigned *md,unsigned *role,unsigned *native_palette,
                         unsigned *md_palette,unsigned *image_ready);
/* A pose using another palette bank is a native draw, not a verified variant. */
unsigned TlkMdSpritesDrawRole(unsigned pose,unsigned palette);
void TlkMdSpritesObserveNpc(unsigned pose,unsigned palette);
int TlkMdSpritesBounds(unsigned pose,int *x,int *y,int *w,int *h);
/* -1 native fallback, 0 transparent, 1 opaque with final RGB555 colour. */
int TlkMdSpritesNpcSample(unsigned pose,int x,int y,unsigned native_pixel,int frames,int palette,
                          const uint16_t *cgram,uint16_t *color);
/* Scene-owned use of a shared drawing in a different verified native bank. */
int TlkMdSpritesNpcSampleBank(unsigned pose,int x,int y,unsigned native_pixel,int frames,int palette,
                          unsigned native_bank,const uint16_t *cgram,uint16_t *color);
/* Captured Hakuna spider only: original bank5 signature, thirteen shared poses. */
int TlkMdSpritesHakunaSpiderSample(unsigned pose,int x,int y,unsigned native_pixel,int frames,int palette,
                                   const uint16_t *cgram,uint16_t *color);
typedef struct TlkMdSpriteExtra { int x,y,c; } TlkMdSpriteExtra;
const TlkMdSpriteExtra *TlkMdSpritesExtras(unsigned pose,unsigned *count);
unsigned TlkMdSpritesCount(void);
/* Unique reviewed native counterpart, zero for absent or ambiguous poses. */
unsigned TlkMdSpritesNativePose(unsigned external_pose);
void TlkMdSpritesReport(const char *path);
#endif
