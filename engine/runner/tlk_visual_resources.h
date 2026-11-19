#ifndef TLK_VISUAL_RESOURCES_H
#define TLK_VISUAL_RESOURCES_H
#include <SDL3/SDL.h>
#include "recomp_runtime_ui.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Modal desktop browser: -1 unavailable, 0 discarded/closed, 1 applied. */
int TlkVisualResourcesOpen(SDL_Window *parent);
/* Paused host settings; callbacks retain the ordinary settings/binding logic. */
int TlkMainSettingsOpen(SDL_Window *parent,RecompRuntimeUi *ui,
                        void (*bind_event)(const SDL_Event *));
extern int (*g_tlk_main_settings_open)(SDL_Window *,RecompRuntimeUi *,void (*)(const SDL_Event *));
/* Optional project module; ordinary non-final hosts retain their editor. */
extern int (*g_tlk_visual_resources_open)(SDL_Window *parent);
#ifdef __cplusplus
}
#endif
#endif
