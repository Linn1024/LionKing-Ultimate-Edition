#ifndef TLK_CONTINUE_TOKEN_ROLE_H
#define TLK_CONTINUE_TOKEN_ROLE_H

/* Reviewed world Continue token. Indexed art is identical, while the original
 * MD frame origins are one row above native. Geometry and identity palette maps
 * belong to the generated reviewed NPC catalog. */
static inline int TlkContinueTokenPose(unsigned pose) {
    switch (pose & 0x3fffff) {
    case 0x6f764: case 0x6f79b: case 0x6f7ce: case 0x6f801: return 1;
    default: return 0;
    }
}

static inline unsigned TlkContinueTokenWord(const unsigned char *r,unsigned a) {
    return r[a]|(unsigned)r[a+1]<<8;
}
static inline unsigned TlkContinueTokenPointer(const unsigned char *r,unsigned a) {
    return TlkContinueTokenWord(r,a)|(unsigned)r[a+2]<<16;
}
/* The collectible program is shared across worlds. Presentation still checks
 * its actual OAM bank and exact native palette before sampling the MD art. */
static inline int TlkContinueTokenCommonDrawRole(const unsigned char *r,unsigned size,
                                               unsigned draw,unsigned pose,int fixed) {
    if (!r || size<0x20000 || fixed || !TlkContinueTokenPose(pose) ||
        draw<0x8000 || draw>0xffe8) return 0;
    unsigned pos=TlkContinueTokenWord(r,draw+4);
    if (pos<0x8008 || pos>0xff88) return 0;
    unsigned actor=pos-8;
    return TlkContinueTokenWord(r,actor+12)==draw &&
        TlkContinueTokenPointer(r,actor+4)==0xc586cc &&
        TlkContinueTokenPointer(r,actor+0x30)==0xc558ff &&
        TlkContinueTokenPose(TlkContinueTokenPointer(r,draw+10));
}

/* Existing Pride timing/audio callers keep their reviewed scene scope. */
static inline int TlkContinueTokenDrawRole(const unsigned char *r,unsigned size,
                                         unsigned draw,unsigned pose,int fixed) {
    if (!r || size<0x20000 || TlkContinueTokenWord(r,0x1ff9e) ||
        TlkContinueTokenWord(r,0x2000)) return 0;
    unsigned scene=TlkContinueTokenPointer(r,0xdf);
    return (scene==0xc00387 || scene==0xc0080d) &&
        TlkContinueTokenCommonDrawRole(r,size,draw,pose,fixed);
}

#endif
