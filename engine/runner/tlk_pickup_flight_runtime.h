#ifndef TLK_PICKUP_FLIGHT_RUNTIME_H
#define TLK_PICKUP_FLIGHT_RUNTIME_H
#include <stdint.h>
#include "cpu_state.h"
int TlkPickupFlightSelected(void);
int TlkPickupFlightProfileChanged(void);
uint32_t TlkPickupFlightOpcode(CpuState *cpu,uint32_t pc);
#endif
