#include "tlk_md_camera.h"
static int clamp(int n,int lo,int hi) { return n<lo?lo:n>hi?hi:n; }
static int signed_word(int n) { unsigned u=(unsigned)n&65535;return u>=32768?(int)u-65536:(int)u; }
static void advance(int *position,uint16_t *fraction,int error,int minimum,int maximum) {
    int velocity=signed_word(error)*8192;
    if (velocity && velocity>-65536 && velocity<65536) velocity=velocity<0?-65536:65536;
    if (velocity>8*65536) *position+=8;
    else if (velocity<-8*65536) *position-=8;
    else {
        int64_t total=(int64_t)*position*65536+*fraction+velocity;
        *position=(int)(total>=0?total/65536:-((-total+65535)/65536));
        *fraction=(uint16_t)total;
    }
    *position=clamp(*position,minimum,maximum);
}
void TlkMdCameraStep(TlkMdCameraState *state,const TlkMdCameraRules *rules,
                     int player_x,int player_y,int facing_left,unsigned flags,int frozen) {
    if (!state || !rules || frozen) return;
    state->look=facing_left?clamp(state->look+1,-32768,rules->look_max):clamp(state->look-1,rules->look_min,32767);
    int horizontal=signed_word(player_x-state->x-state->look);
    if(rules->forward_only && horizontal<0)horizontal=0;
    advance(&state->x,&state->fraction_x,horizontal,rules->min_x,rules->max_x);
    state->target_y=flags&2?rules->up_y:flags&1?rules->down_y:rules->target_y;
    int error=signed_word(player_y-state->y-state->target_y);
    if (!(flags&3)) error=error<0?clamp(error+rules->deadzone_y,-32768,0):clamp(error-rules->deadzone_y,0,32767);
    advance(&state->y,&state->fraction_y,error,rules->min_y,rules->max_y);
}
