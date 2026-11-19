#ifndef TLK_PRIDE_SAVE_CONTEXT_H
#define TLK_PRIDE_SAVE_CONTEXT_H

/* Snapshot used only to choose the ordinary private-save path. This is not a
 * serialized record. A positive result still requires the renderer and full
 * preparation cache validators before any file is published. */
typedef struct TlkPrideSaveContext {
    unsigned owner_installed, restore_installed, have_return;
    unsigned owner_started, preparation_pending;
    unsigned owner_waiting, grounded_waiting, scene_active, active;
    unsigned level, descriptor, cub_age, health, word_1ff90, phase;
} TlkPrideSaveContext;

static inline int TlkPrideIdleSaveEligible(const TlkPrideSaveContext *context) {
    if (!context || !context->owner_installed || !context->restore_installed ||
        !context->have_return || context->owner_started || context->preparation_pending ||
        context->owner_waiting || context->grounded_waiting || context->scene_active ||
        context->active || context->level || context->cub_age || !context->health ||
        context->word_1ff90 || (context->phase != 4 && context->phase != 6))
        return 0;
    /* C005AB is the native card, not an MD-rendered play scene. Eligibility
     * preserves its complete idle cache; it does not grant any capability. */
    return context->descriptor == 0xc00387 || context->descriptor == 0xc0080d ||
           context->descriptor == 0xc005ab;
}

#endif
