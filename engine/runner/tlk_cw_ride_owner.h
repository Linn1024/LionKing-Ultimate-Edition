#ifndef TLK_CW_RIDE_OWNER_H
#define TLK_CW_RIDE_OWNER_H
#include <stddef.h>
#include <stdint.h>

static inline unsigned TlkCwRideWord(const uint8_t *p) {return p[0]|(unsigned)p[1]<<8;}
static inline unsigned TlkCwRidePointer(const uint8_t *p) {return TlkCwRideWord(p)|(unsigned)p[2]<<16;}
static inline int TlkCwRidePose(unsigned pose) {
    return pose==0xc45a16 || pose==0xc3b6f7 || pose==0xc3b756 ||
           pose==0xc3b77b || pose==0xc3b7f2;
}
/* A branch is a child draw whose position lives at parent+5A. The ordinary
 * actor backlink applies to its collision drawing, not to the branch. Resolve
 * this at submission time; later parent/draw heap reuse must not recolor it. */
static inline unsigned TlkCwRideDrawDescriptor(const uint8_t *ram,size_t size,
        const uint8_t *rom,size_t rom_size,unsigned draw,unsigned pose) {
    if(!ram || size<0x20000 || !rom || rom_size<0x4e1b9 ||
       draw<0x8000 || draw>0xffe8 || !TlkCwRidePose(pose) ||
       TlkCwRidePointer(ram+draw+10)!=pose)return 0;
    unsigned position=TlkCwRideWord(ram+draw+4);
    int child=pose==0xc3b6f7 || pose==0xc3b77b;
    unsigned offset=child?0x5a:8;
    if(position<0xa000+offset || position>0xff80)return 0;
    unsigned actor=position-offset,descriptor=TlkCwRidePointer(ram+actor+4);
    unsigned program=0,head=0;
    if(descriptor==0xc4e18d) {program=0xc42fae;head=0xc45a16;}
    if(descriptor==0xc4e198 || descriptor==0xc4e1ae) {program=0xc42cde;head=0xc3b756;}
    if(descriptor==0xc4e1a3) {program=0xc42e46;head=0xc3b7f2;}
    if(!program || (child?(pose==0xc3b6f7?head!=0xc3b756:head!=0xc3b7f2):pose!=head))return 0;
    unsigned at=descriptor&0x3fffff;
    if(TlkCwRidePointer(rom+at)!=program || TlkCwRidePointer(rom+at+8)!=head)return 0;
    if(child) {
        unsigned parent_draw=TlkCwRideWord(ram+actor+12);
        if(TlkCwRidePointer(ram+actor+0x56)!=(0x7e0000|draw) ||
           parent_draw<0x8000 || parent_draw>0xffe8 ||
           TlkCwRideWord(ram+parent_draw+4)!=actor+8 ||
           TlkCwRidePointer(ram+parent_draw+10)!=head)return 0;
    } else if(TlkCwRideWord(ram+actor+12)!=draw)return 0;
    return descriptor;
}
#endif
