#ifndef TLK_CONTACT_SEARCH_H
#define TLK_CONTACT_SEARCH_H
#include "cpu_state.h"
/* Same bounded tail step for the native loop and original interpreter seams.
 * Return zero when the source call must keep its ordinary behavior. */
unsigned TlkContactSearchTailStep(CpuState *cpu,unsigned pc);
#endif
