#ifndef TLK_GUEST_H
#define TLK_GUEST_H
#include "cpu_state.h"
/* Delegate original bytes with the caller's existing hardware return frame.
 * Use a full 24-bit entry for cross-bank compiled calls (PB may be the caller). */
RecompReturn TlkRunOriginal(CpuState *cpu,unsigned entry,unsigned frame_size);
#endif
