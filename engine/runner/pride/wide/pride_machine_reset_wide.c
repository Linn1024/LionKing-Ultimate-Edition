/* Machine reset discards presentation history; immutable decoded art survives. */
#include "pride_restart_wide.c"
void PrideMachineRendererReset(const char *folder) {
    if(prepared_changed || scene_palette_active || scene_tag_mode)exit(95);
    PrideRestartRendererReset(folder);
    scene_health_age=270;scene_ready_age=345;
    scene_width=scene_column=scene_y_offset=scene_flipx=0;
    scene_background_field=scene_palette_age=0;
    memset(scene_previous_camera,0,sizeof scene_previous_camera);
    memset(scene_background,0,sizeof scene_background);
    memset(scene_cgram,0,sizeof scene_cgram);
    memset(scene_unfaded,0,sizeof scene_unfaded);
    memset(scene_previous_frame,0,sizeof scene_previous_frame);
    memset(scene_current_frame,0,sizeof scene_current_frame);
    memset(scene_previous_vram,0,sizeof scene_previous_vram);
    memset(scene_current_vram,0,sizeof scene_current_vram);
    memset(scene_full_base,0,sizeof scene_full_base);
    memset(scene_base_tags,0,sizeof scene_base_tags);
    memset(scene_background_tags,0,sizeof scene_background_tags);
    memset(scene_native_output,0,sizeof scene_native_output);
    memset(prepared_frame,0,sizeof prepared_frame);
    memset(prepared_vram,0,sizeof prepared_vram);
}
