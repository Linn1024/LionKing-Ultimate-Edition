#ifndef TLK_PICKUP_FLIGHT_MOTION_H
#define TLK_PICKUP_FLIGHT_MOTION_H
#include <stdbool.h>
#include <stdint.h>

/* Arithmetic between the existing action's animation and reward calls.
 * Initialization takes screen coordinates. The caller retains original
 * animation, ownership, reward, retirement and scene scheduling. */
typedef struct TlkPickupFlightMotion {
    uint16_t x,y,step;
} TlkPickupFlightMotion;

bool TlkPickupFlightBegin(TlkPickupFlightMotion *motion,uint16_t x,uint16_t y,
                        uint16_t target_x,uint16_t target_y);
/* Apply the original animation's signed X displacement after adding step. */
bool TlkPickupFlightAdvance(TlkPickupFlightMotion *motion,uint16_t target_x,
                          uint16_t target_y,int animation_dx,bool right);
#endif
