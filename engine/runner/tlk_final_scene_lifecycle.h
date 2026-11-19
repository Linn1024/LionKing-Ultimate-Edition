#ifndef TLK_FINAL_SCENE_LIFECYCLE_H
#define TLK_FINAL_SCENE_LIFECYCLE_H
#include "tlk_continue_scene.h"

/* The caller must independently establish a new ordinary final-life entry.
 * Completed Pride reloads also establish a previous playable episode when a
 * cold bank forced native Continue timing and no owned Continue clock began.
 * An unfinished/saved first-entry boundary must not rearm itself. */
static inline int TlkFinalSceneRearmReady(uint32_t previous_entry,unsigned reload_mask,
                                         const TlkContinueScene *continuation,uint64_t field) {
    if(!previous_entry || field<=previous_entry || (reload_mask&~511u))return 0;
    if(reload_mask==511u)return 1;
    TlkContinueView view;
    return continuation && TlkContinueSceneView(continuation,field,&view) && view.controls_ready;
}
#endif
