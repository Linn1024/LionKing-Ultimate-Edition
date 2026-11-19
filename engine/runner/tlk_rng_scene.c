#include "tlk_rng_scene.h"
#include <string.h>
static unsigned word(const uint8_t *r,unsigned a) { return r[a]|(unsigned)r[a+1]<<8; }
int TlkRngSceneDataInit(TlkRngSceneData *d,const uint8_t *s,size_t sn,const uint8_t *m,size_t mn) {
    if(!d)return 0;memset(d,0,sizeof *d);
    if(!s || !m || sn!=0x300000 || mn!=0x300000 ||
       memcmp(s+0x7970,"\x9e\x00\x00\xca\xe0\xff\x02\xd0",8))return 0;
    uint32_t seed=0;
    for(unsigned i=0;i<3;i++) {
        const uint8_t *p=m + 0x1d77de + i*8;
        if(p[0]!=0x13 || p[1]!=0xfc || p[2] || p[4]!=0xff || p[5]!=0xff || p[6]!=0x81 || p[7]!=0xad+i)return 0;
        seed=seed<<8|p[3];
    }
    d->normal_seed=seed;d->ready=1;return 1;
}
int TlkRngSceneStep(const TlkRngSceneData *d,CpuState *c,uint32_t pc,uint8_t *r,size_t n,int selected) {
    if(!d || !d->ready || !c || !r || n!=0x20000 || !selected ||
       c->PB!=0xc0 || c->D || (c->DB!=0 && c->DB!=0x7e) || c->emulation || c->m_flag || c->x_flag ||
       word(r,0x1ff9e) || word(r,0x1ffa2))return 0;
    pc&=0xffffff;unsigned descriptor=word(r,0xdf)|(unsigned)r[0xe1]<<16;
    if(pc==0xc07979 && !descriptor && c->X==0x2ff && !c->A) {
        /* Normal Pride entry/Continue. Original MD seeds before its first
         * random call; native scene clearing has already completed here. */
        r[0x1e00]=(uint8_t)d->normal_seed;r[0x1e01]=(uint8_t)(d->normal_seed>>8);r[0x1e02]=(uint8_t)(d->normal_seed>>16);
        return 1;
    }
    if((descriptor!=0xc00387 && descriptor!=0xc0080d) || c->X!=0x1dff)return 0;
    if(pc==0xc07970 && !c->A) {
        /* The original A is known zero from LDA checkpoint/BNE. STZ does not
         * read A or change flags. Carry the overwritten byte in the CPU's A,
         * so an intervening field/save/interrupt needs no host pending flag. */
        c->A=r[0x1e00];return 1;
    }
    if(pc==0xc07973 && c->A<=255 && !r[0x1e00]) {
        r[0x1e00]=(uint8_t)c->A;c->A=0;return 1;
    }
    return 0;
}
