#ifndef TLK_MD_CAMERA_H
#define TLK_MD_CAMERA_H
#include <stdint.h>
typedef struct TlkMdCameraState { int x,y,look,target_y;uint16_t fraction_x,fraction_y; } TlkMdCameraState;
typedef struct TlkMdCameraRules { int min_x,max_x,min_y,max_y,look_min,look_max,target_y,down_y,up_y,deadzone_y,forward_only; } TlkMdCameraRules;
/* Arithmetic only. A gameplay adapter must coordinate viewport/guest conventions. */
void TlkMdCameraStep(TlkMdCameraState *state,const TlkMdCameraRules *rules,
                     int player_x,int player_y,int facing_left,unsigned flags,int frozen);
#endif
