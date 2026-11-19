#ifndef TLK_TITLE_ROLE_H
#define TLK_TITLE_ROLE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
static inline unsigned TlkTitleWord(const uint8_t *r,unsigned a){return r[a]|(unsigned)r[a+1]<<8;}
static inline uint32_t TlkTitlePointer(const uint8_t *r,unsigned a){return TlkTitleWord(r,a)|(uint32_t)r[a+2]<<16;}
/* The dynamic WRAM packet is reused for other strings. Validate its complete
 * original first-line content, not just its address or the generic text task. */
static inline bool TlkPrideTitleDrawRole(const uint8_t *ram,size_t size,const uint8_t *rom,size_t rs,
                                        unsigned draw,uint32_t pose,bool fixed) {
    if(!ram || size<0x20000 || !rom || rs<0x3bca6 || fixed || pose!=0x7e17dd ||
       draw<0x8000 || draw>0xffe8 || TlkTitleWord(ram,0x1ff9e) || TlkTitleWord(ram,0x2000))return false;
    uint32_t scene=TlkTitlePointer(ram,0xdf);
    if(scene!=0xc00387 && scene!=0xc0080d)return false;
    unsigned pos=TlkTitleWord(ram,draw+4);if(pos<0x8008 || pos>0xff88)return false;
    unsigned actor=pos-8;
    if(TlkTitleWord(ram,actor+12)!=draw || TlkTitlePointer(ram,draw+10)!=pose ||
       TlkTitlePointer(ram,actor+4)!=0xc588cb || TlkTitlePointer(ram,actor+0x30)!=0xc0679e ||
       (ram[draw+8]&14) || (ram[draw+9]&0x40) || TlkTitleWord(ram,actor+0x2c)>150)return false;
    unsigned packet=pose&65535;
    if(TlkTitleWord(ram,packet)!=13 || TlkTitleWord(ram,packet+6)!=224 ||
       TlkTitleWord(ram,packet+8)!=255 || ram[packet+26]!=0xe8 || rom[0x3bc97+14]!=13)return false;
    int last=(int16_t)TlkTitleWord(ram,packet+27+12*6+2);
    if(last>0 || last<-128)return false;
    unsigned n=0;
    for(unsigned i=0;i<14;i++) {
        unsigned c=rom[0x3bc97+i];if(c==' ')continue;
        if(c<'A' || c>'Z')return false;
        unsigned at=packet+27+n*6;
        int y=last+4*(12-(int)n);if(y>0)y=0;
        if(TlkTitleWord(ram,at)!=i*16 || (int16_t)TlkTitleWord(ram,at+2)!=y ||
           TlkTitleWord(ram,at+4)!=0x88ef+(c-'A')*128)return false;
        n++;
    }
    return n==13;
}
#endif
