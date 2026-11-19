#ifndef PRIDE_SCENE_RENDER_BRIDGE_H
#define PRIDE_SCENE_RENDER_BRIDGE_H
#include "tlk_death_scene.h"
/* Research host only. Returns the current controller without transferring
 * guest ownership to the presenter. No function mutates guest state. */
int PrideSceneRenderView(TlkDeathScene *scene,TlkDeathProgram *program);
/* Read-only metadata of the original native roar callback's last actual
 * rebuild. Cache-hit scratch is not a new font context. */
int PrideSceneRestoreRoarContext(unsigned maximum,unsigned current,uint16_t *initial_full);
#endif
