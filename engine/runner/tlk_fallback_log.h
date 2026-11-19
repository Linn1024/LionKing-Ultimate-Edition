#ifndef TLK_FALLBACK_LOG_H
#define TLK_FALLBACK_LOG_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Diagnostics only. No guest state, source choice or playback is changed.
 * Repeated occurrences are counted within each frame, not hidden for a session. */
int TlkFallbackEnabled(void);
typedef struct TlkFallbackSpriteInfo {
    unsigned descriptor,latched_descriptor,actor,action,owner_valid;
    unsigned mapped_pose,mapped_role,scene_role,image_ready;
    unsigned frames_md,palette_md,native_palette,md_palette,attributes,size,draw_width;
    unsigned pose_header_fnv32,tile_fnv32,palette_fnv32;
    int actor_x,actor_y,player_x,player_y,camera_x,camera_y,screen_x,screen_y,local_x,local_y;
} TlkFallbackSpriteInfo;
/* Sample-stage context is borrowed only during the sprite sampler call. */
void TlkFallbackSpriteContext(const TlkFallbackSpriteInfo *info);
void TlkFallbackSpriteRecord(const char *kind,const char *reason,unsigned object,unsigned pose,
                             const TlkFallbackSpriteInfo *info,uint64_t count);
void TlkFallbackContext(unsigned field,unsigned level,unsigned scene);
void TlkFallbackRecord(const char *kind,const char *resource,const char *reason,
                       unsigned object,unsigned pose,unsigned detail,uint64_t count);
void TlkFallbackFlush(void);
/* A complete later host canvas replaces the native compositor underlay. */
void TlkFallbackCanvasOwned(unsigned field);
#ifdef __cplusplus
}
#endif
#endif
