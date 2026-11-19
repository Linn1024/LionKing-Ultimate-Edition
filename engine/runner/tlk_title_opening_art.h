#ifndef TLK_TITLE_OPENING_ART_H
#define TLK_TITLE_OPENING_ART_H
#include <stddef.h>
#include <stdint.h>
typedef struct TlkTitleOpeningArt TlkTitleOpeningArt;
/* Validated installation data only. Age0 is the first title backdrop/logo;
 * original Simba submissions begin at age2. Last pose is held for the menu. */
TlkTitleOpeningArt *TlkTitleOpeningArtLoad(const uint8_t *,size_t);
void TlkTitleOpeningArtFree(TlkTitleOpeningArt *);
int TlkTitleOpeningArtBackdrop(const TlkTitleOpeningArt *,uint32_t *);
int TlkTitleOpeningArtDraw(const TlkTitleOpeningArt *,unsigned,uint32_t *);
#endif
