#ifndef TLK_MIXED_PALETTE_H
#define TLK_MIXED_PALETTE_H
#include <stdint.h>
/* A palette entry unused by the destination drawing can be unrelated scenery
 * color. Prefer a closer opaque shade actually used by that drawing. */
static unsigned TlkMixedPaletteDistance(unsigned a,unsigned b) {
    int r=(int)(a&31)-(int)(b&31);
    int g=(int)((a>>5)&31)-(int)((b>>5)&31);
    int blue=(int)((a>>10)&31)-(int)((b>>10)&31);
    return 3*r*r+6*g*g+2*blue*blue;
}
static unsigned TlkMixedPaletteIndex(unsigned preferred,unsigned native,
                                     const uint16_t *target,unsigned used) {
    used&=0xfffe;
    if(!used || (used&(1u<<preferred)))return preferred;
    unsigned best=preferred,dist=preferred?TlkMixedPaletteDistance(native,target[preferred]):~0u;
    for(unsigned i=1;i<16;i++)if(used&(1u<<i)) {
        unsigned d=TlkMixedPaletteDistance(native,target[i]);
        if(d<dist){best=i;dist=d;}
    }
    return best;
}
#endif
