#ifndef TLK_CONTINUE_MENU_H
#define TLK_CONTINUE_MENU_H
#include <stdint.h>
/* Original MD ordinary Continue. These are displayed-field ages from the
 * fatal entry, not elapsed CPU cycles or the native credit-dependent timer.
 * Direction changes do not extend the window. The final confirm at844 is
 * accepted;845 and later retain the ordinary timeout-to-title path. */
enum { TLK_CONTINUE_MENU_FIRST_INPUT=124, TLK_CONTINUE_MENU_TIMEOUT=845,
       TLK_GAME_OVER_MENU_TIMEOUT=324 };
static inline int TlkContinueMenuTimedOut(uint32_t age) {
    return age>=TLK_CONTINUE_MENU_TIMEOUT;
}
/* Original MD Game Over accepts the same first input, then leaves without
 * credits at324 (first dim picture325, black343). It is not Continue's timer. */
static inline int TlkGameOverMenuTimedOut(uint32_t age) {
    return age>=TLK_GAME_OVER_MENU_TIMEOUT;
}
#endif
