#ifndef TLK_FINAL_SCENE_STATE_H
#define TLK_FINAL_SCENE_STATE_H
#include <stddef.h>
#include <stdint.h>
#include "tlk_continue_scene.h"
#include "tlk_title_navigation.h"

enum {
    TLK_FINAL_ONCE=1,TLK_FINAL_FAST_ASSETS=2,TLK_FINAL_ORIGIN=4,
    TLK_FINAL_TARGET=8,TLK_FINAL_WAITING=16,TLK_FINAL_LEVEL=32,
    TLK_FINAL_INPUT_STARTED=64,TLK_FINAL_TITLE_EXIT=128,TLK_FINAL_MENU_CANVAS=256,
    TLK_FINAL_CANVAS_PIXELS=256*224,
    TLK_FINAL_STATE_BYTES=192+4*TLK_FINAL_CANVAS_PIXELS*4
};
/* Pointer-free runtime state. Install flags, callbacks, files, decoder scratch
 * and source assets are process-owned, not serialized. Canvas order is original
 * fatal picture, menu target, retained outgoing menu, unfaded incoming level. */
typedef struct TlkFinalSceneState {
    uint32_t field,entry_field,age,flags,reload_used;
    uint32_t wait_a,wait_x,wait_y,wait_s,wait_d,wait_p,wait_db,input_stage;
    TlkContinueScene continuation;
    uint32_t menu_field,title_fade_field,menu_credits;
    uint32_t title_ready_field,title_previous_pad;
    TlkTitleNavigation title_navigation;
    uint32_t canvas[4][TLK_FINAL_CANVAS_PIXELS];
} TlkFinalSceneState;
void TlkFinalSceneStateClear(TlkFinalSceneState *state);
int TlkFinalSceneStateValid(const TlkFinalSceneState *state);
/* Exact, versioned, little-endian record with source identity and SHA256.
 * Failure leaves the output/state unchanged. Caller owns complete runtime and
 * native/bank validation before committing a combined game save. */
int TlkFinalSceneStateSave(const TlkFinalSceneState *state,const uint8_t source[32],uint8_t *out,size_t size);
int TlkFinalSceneStateLoad(TlkFinalSceneState *state,const uint8_t source[32],const uint8_t *data,size_t size);
#endif
