#ifndef TLK_DEATH_SCENE_H
#define TLK_DEATH_SCENE_H
#include <stddef.h>
#include <stdint.h>

/* The controller owns the original MD video clock, not native opcode calls.
 * Coordinates are in the original 320-column scene space. A host adapter must
 * translate its viewport origin and prepare native scene data separately. */
enum { TLK_DEATH_TOKENS=33, TLK_REVIVAL_TOKENS=12, TLK_DEATH_SCENE_RECORD_SIZE=128 };
typedef struct TlkDeathToken { uint32_t snes_pose,md_pose; uint8_t duration; } TlkDeathToken;
typedef struct TlkDeathProgram {
    TlkDeathToken tokens[TLK_DEATH_TOKENS];
    TlkDeathToken revival[TLK_REVIVAL_TOKENS],idle;
    uint8_t identity[32];
    uint32_t ready;
} TlkDeathProgram;
typedef struct TlkDeathScene {
    uint64_t last_field,owner;
    uint16_t origin_x,origin_y,camera_x,camera_y,age;
    uint8_t started,final_life,has_checkpoint;
} TlkDeathScene;
typedef struct TlkDeathContext {
    unsigned md_selected,level,descriptor,cub_age,health,skip_display,actor; /* descriptor is full24bit */
    uint32_t state_marker,entry_pc;
    uint64_t owner;
    uint16_t x,y,camera_x,camera_y;
    /* Caller supplies normalized life/checkpoint decisions, not raw counters
     * from the other console. Entry ownership is checked independently. */
    unsigned final_life,has_checkpoint;
} TlkDeathContext;
enum TlkDeathPhase {
    TLK_DEATH_NONE,TLK_DEATH_SCENERY_FADE,TLK_DEATH_DISPLAY,
    TLK_DEATH_ACTOR_FADE,TLK_DEATH_RELOAD,TLK_DEATH_REVIVAL_FADE,TLK_DEATH_REVIVAL_HOLD,
    TLK_DEATH_READY,TLK_DEATH_GAME_OVER
};
enum {
    TLK_DEATH_EVENT_DISPLAY_END=1,TLK_DEATH_EVENT_BLACK=2,
    TLK_DEATH_EVENT_RESTORE_HEALTH=4,TLK_DEATH_EVENT_READY=8,
    TLK_DEATH_EVENT_GAME_OVER=16,TLK_DEATH_EVENT_REPLACE_ACTOR=32,TLK_DEATH_EVENT_REVIVAL_HOLD=64
};
typedef struct TlkDeathView {
    enum TlkDeathPhase phase;
    uint16_t age,x,y;
    unsigned token,timer;
    uint32_t snes_pose,md_pose;
} TlkDeathView;
/* Replacement artwork has its own placement, supplied by the prepared native
 * checkpoint scene. Do not reuse the dead actor's centered coordinates. */
typedef struct TlkDeathRevivalView {
    unsigned prepared,checkpoint_animation,token,timer;
    uint32_t snes_pose,md_pose,md_cursor;
} TlkDeathRevivalView;

/* Full pinned ROM identities and paired stream/loop bounds are validated.
 * A successful program is immutable for the lifetime of its scenes. */
int TlkDeathProgramInit(TlkDeathProgram *out,const uint8_t *snes,size_t snes_size,
                       const uint8_t *md,size_t md_size);
void TlkDeathSceneReset(TlkDeathScene *scene);
/* Rejects unsupported contexts and active scene reentry without mutation. */
int TlkDeathSceneBegin(TlkDeathScene *scene,const TlkDeathProgram *program,
                      const TlkDeathContext *context,uint64_t field,unsigned *events);
/* Exactly one call per new field. Duplicate calls are idempotent; skipped or
 * reversed fields reject without mutation. Host pause advances the field ID
 * without advancing the scene. Events are delivered once at their boundary. */
int TlkDeathSceneAdvance(TlkDeathScene *scene,const TlkDeathProgram *program,
                        uint64_t field,unsigned paused,unsigned *events);
int TlkDeathSceneView(const TlkDeathScene *scene,const TlkDeathProgram *program,TlkDeathView *view);
/* Original checkpoint pose is held during fade-in, then advanced in the49-field
 * respawn loop. Default revival retains idle artwork, with its own timer. */
int TlkDeathSceneRevivalView(const TlkDeathScene *scene,const TlkDeathProgram *program,TlkDeathRevivalView *view);
/* Packed original MD3bit RGB. Palette ownership is explicit; the eventual
 * renderer must map semantic colors for SNES-selected artwork separately. */
int TlkDeathScenePalette(const TlkDeathScene *scene,const TlkDeathProgram *program,
                        unsigned index,unsigned death_color,unsigned next_color,uint16_t *color);
/* Independent versioned record for future outer-state integration. Load is
 * atomic, source-bound and rejects invalid/reserved state before publication. */
int TlkDeathSceneSave(const TlkDeathScene *scene,const TlkDeathProgram *program,uint8_t *out,size_t size);
int TlkDeathSceneLoad(TlkDeathScene *scene,const TlkDeathProgram *program,const uint8_t *data,size_t size);
#endif
