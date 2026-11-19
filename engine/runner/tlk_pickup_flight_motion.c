#include "tlk_pickup_flight_motion.h"

static int signed_word(uint16_t value) {
    return value<0x8000u?(int)value:(int)value-65536;
}
bool TlkPickupFlightBegin(TlkPickupFlightMotion *motion,uint16_t x,uint16_t y,
                         uint16_t target_x,uint16_t target_y) {
    if(!motion)return false;
    int dx=signed_word((uint16_t)(target_x-x));
    int dy=signed_word((uint16_t)(y-target_y));
    int step=dx;
    if(dy>0) {
        int divisor=dy/2;
        /* Original 68k DIVS traps for a zero divisor. Do not replace that
         * unsupported initialization with an invented flight. */
        if(!divisor)return false;
        step=dx/divisor;
    }
    motion->x=x;motion->y=y;motion->step=(uint16_t)step;
    return true;
}
bool TlkPickupFlightAdvance(TlkPickupFlightMotion *motion,uint16_t target_x,
                           uint16_t target_y,int animation_dx,bool right) {
    if(!motion)return false;
    uint16_t x=(uint16_t)((unsigned)motion->x+motion->step+(uint16_t)animation_dx);
    int relation=signed_word((uint16_t)(x-target_x));
    if((right && relation>0) || (!right && relation<0))x=target_x;
    motion->x=x;
    if(signed_word((uint16_t)(motion->y-target_y))>0) {
        motion->y=(uint16_t)(motion->y-2);return false;
    }
    motion->y=target_y;
    relation=signed_word((uint16_t)(target_x-x));
    motion->step=(uint16_t)(relation>0?3:relation<0?-3:0);
    int distance=signed_word((uint16_t)(x-target_x));
    if(distance<0)distance=-distance;
    return distance<8;
}
