#ifndef TLK_CONTINUE_SCENE_H
#define TLK_CONTINUE_SCENE_H
#include <stdint.h>

typedef enum TlkContinuePhase {
    TLK_CONTINUE_MENU,TLK_CONTINUE_FADE_OUT,TLK_CONTINUE_BLACK,
    TLK_CONTINUE_FADE_IN,TLK_CONTINUE_LEVEL
} TlkContinuePhase;
typedef struct TlkContinueScene {
    uint64_t confirmed_field;
    uint32_t origin_descriptor;
} TlkContinueScene;
typedef struct TlkContinueView {
    TlkContinuePhase phase;
    unsigned step,controls_ready;
} TlkContinueView;
/* Confirmed YES only; the caller owns the final-life/menu lifecycle. No guest,
 * audio, renderer or resource state is changed by this presentation clock. */
int TlkContinueSceneBegin(TlkContinueScene *scene,uint32_t origin,uint64_t field);
int TlkContinueSceneView(const TlkContinueScene *scene,uint64_t field,TlkContinueView *view);
/* Original MD three-bit component operation, independent of selected artwork. */
unsigned TlkContinueSceneMdComponent(const TlkContinueView *view,unsigned component);
/* Native five-bit palette projection: preserve all native colours at full
 * visibility, normalized seven-step clipping/subtraction at MD phase times. */
unsigned TlkContinueSceneNativeComponent(const TlkContinueView *view,unsigned component);
#endif
