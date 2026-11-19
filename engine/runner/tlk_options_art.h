#ifndef TLK_OPTIONS_ART_H
#define TLK_OPTIONS_ART_H
#include <stddef.h>
#include <stdint.h>
typedef struct TlkOptionsArt TlkOptionsArt;
/* Prepared original MD Options artwork only. Input, actual settings, audition
 * submenus and scene ownership belong to the host; no ROM reads or fallback. */
TlkOptionsArt *TlkOptionsArtLoad(const uint8_t *record,size_t size);
void TlkOptionsArtFree(TlkOptionsArt *art);
int TlkOptionsArtDraw(const TlkOptionsArt *art,unsigned selected,unsigned bob_x,
    unsigned difficulty,unsigned music,unsigned effects,unsigned configuration,uint32_t *out);
/* Independent input bindings can use the same original MD font without
 * claiming that native preset numbers describe MD's different control table.
 * Button order is roar, adult slash, jump. Characters must be actual bindings. */
int TlkOptionsArtDrawBindings(const TlkOptionsArt *art,unsigned selected,unsigned bob_x,
    unsigned difficulty,unsigned music,unsigned effects,const char buttons[3],uint32_t *out);
/* Shared installed font/palette/selector over the independently prepared
 * Sound Test backdrop and sixteen 18-byte catalogue records. */
int TlkOptionsArtDrawSoundTest(const TlkOptionsArt *,const uint8_t *,const uint8_t *,
    unsigned,unsigned,uint32_t *);
int TlkOptionsArtDrawDebugMenu(const TlkOptionsArt *,const uint8_t *,const uint8_t *,
    unsigned,unsigned,unsigned,unsigned,uint32_t *);
int TlkOptionsArtDrawSoundTestRows(const TlkOptionsArt *,const uint8_t *,const char [7][21],unsigned,uint32_t *);
#endif
