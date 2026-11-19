#ifndef TLK_TITLE_NAVIGATION_H
#define TLK_TITLE_NAVIGATION_H
#include <stdint.h>
typedef struct TlkTitleNavigation {
    uint32_t owner,next_field,previous_pad;
} TlkTitleNavigation;
void TlkTitleNavigationClear(TlkTitleNavigation *state);
/* MD two-choice input sampling: directions precede confirmation; sampling
 * pauses for nine fields after navigation. Native ready input seeds first use. */
uint16_t TlkTitleNavigationInput(TlkTitleNavigation *state,uint32_t field,
    uint16_t owner,uint16_t held,uint16_t native_input,unsigned selection);
int TlkTitleNavigationValid(const TlkTitleNavigation *state,uint32_t field);
#endif
