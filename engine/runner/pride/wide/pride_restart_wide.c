/* Restart extension; the verified repeated-revival presenter remains intact. */
#include <stdlib.h>
#include <string.h>
static char restart_render_folder[4096];
static char *restart_getenv(const char *name) {
    if(restart_render_folder[0] && !strcmp(name,"TLK_SCENE_RENDER_PROBE"))return restart_render_folder;
    return getenv(name);
}
#define getenv restart_getenv
#include "pride_repeat_state_wide.c"
#undef getenv
uint32_t PrideCurrentGraphicsChoices(void) { return history_graphics(); }
int PrideRestartRendererReady(void) {
    return !prepared_changed && !scene_palette_active && !scene_tag_mode;
}
void PrideRestartRendererReset(const char *folder) {
    if(scene_render_log)fclose(scene_render_log);scene_render_log=NULL;
    if(scene_rgb_trace)fclose(scene_rgb_trace);scene_rgb_trace=NULL;
    if(prepared_events)fclose(prepared_events);prepared_events=NULL;
    if(prepared_font_trace)fclose(prepared_font_trace);prepared_font_trace=NULL;
    snprintf(restart_render_folder,sizeof restart_render_folder,"%s",folder);
    scene_epoch_field=0;scene_mode=-1;scene_draws=scene_released=0;
    scene_have_background=scene_previous_valid=scene_normal_actor=0;
    prepared_count=prepared_hud=prepared_age=0;
    memset(prepared_pieces,0,sizeof prepared_pieces);memset(prepared_cub,0,sizeof prepared_cub);
    memset(prepared_health,0,sizeof prepared_health);memset(prepared_roar,0,sizeof prepared_roar);
}
