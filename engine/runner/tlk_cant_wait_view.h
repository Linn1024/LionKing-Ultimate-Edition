#ifndef TLK_CANT_WAIT_VIEW_H
#define TLK_CANT_WAIT_VIEW_H
#include "tlk_md_assets.h"
#include <string.h>
/* Plane B presentation state only. Original MD18D764 starts on the level's
 * palette trigger and18D79E steps channels every nine updates. The native
 * matching palette event supplies that trigger; it never receives writes. */
typedef struct TlkCantWaitView {
    unsigned active,triggered,delay,updates,latch;
    unsigned camera,previous_camera,wrap,previous_wrap;
    uint16_t colors[100];
} TlkCantWaitView;
static void TlkCantWaitViewUpdate(TlkCantWaitView *view,int scene,int checkpoint,
                                 int trigger,int paused,unsigned latch,unsigned camera,unsigned wrap) {
    if(!scene || !TlkMdCantWaitReady()){memset(view,0,sizeof *view);return;}
    if(!view->active) {
        memset(view,0,sizeof *view);
        if(!TlkMdCantWaitInitialPalette(checkpoint?1:0,view->colors))return;
        view->active=1;view->latch=latch;
        view->camera=view->previous_camera=camera&65535;
        view->wrap=view->previous_wrap=wrap&65535;
    }
    if(paused || view->latch==latch)return;
    view->latch=latch;view->camera=view->previous_camera;view->wrap=view->previous_wrap;
    view->previous_camera=camera&65535;view->previous_wrap=wrap&65535;
    if(!view->triggered && trigger){view->triggered=1;view->delay=1;}
    if(view->triggered && view->updates<100) {
        view->updates++;
        if(view->delay)view->delay--;
        else {TlkMdCantWaitPaletteStep(view->colors);view->delay=8;}
    }
}
#endif
