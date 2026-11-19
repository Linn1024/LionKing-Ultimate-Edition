#ifndef TLK_OPTIONS_ART_INTERNAL_H
#define TLK_OPTIONS_ART_INTERNAL_H
#include "tlk_options_art.h"
enum { OPTIONS_PIXELS=320*224,OPTIONS_PAYLOAD=128+320*224+96*64+24*24+18,OPTIONS_RECORD=112+OPTIONS_PAYLOAD };
struct TlkOptionsArt {uint16_t palette[64];uint8_t base[OPTIONS_PIXELS],font[96][64],selector[576],buttons[6][3];};
#endif
