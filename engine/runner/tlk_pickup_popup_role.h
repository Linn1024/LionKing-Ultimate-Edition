#ifndef TLK_PICKUP_POPUP_ROLE_H
#define TLK_PICKUP_POPUP_ROLE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Reviewed HUD arrivals only. A matching pose in an unrelated fixed object
 * must not inherit the popup palette, animation or anchor translation. */
static inline bool TlkPickupPopupDrawRole(const uint8_t *ram,size_t size,
                                         unsigned draw,uint32_t pose,bool fixed) {
    static const uint32_t poses[]={0xc6fd06,0xc6fd29,0xc6fd4c,0xc6fd73,
        0xc6fd94,0xc6fdbb,0xc6fde6,0xc6fe0b,0xc6fe30,0xc6fe55,0xc6fe7c,0xc6fe9d};
    if(!fixed || !ram || size<0x20000 || draw<0x8000 || draw>0xffe8)return false;
    unsigned i=0;for(;i<sizeof poses/sizeof poses[0];i++)if(pose==poses[i])break;
    if(i==sizeof poses/sizeof poses[0])return false;
    uint32_t scene=ram[0xdf]|(uint32_t)ram[0xe0]<<8|(uint32_t)ram[0xe1]<<16;
    if(ram[0x1ff9e] || ram[0x1ff9f] || ram[0x2000] || ram[0x2001] ||
       (scene!=0xc00387 && scene!=0xc0080d))return false;
    unsigned position=ram[draw+4]|(unsigned)ram[draw+5]<<8;
    if(position<0x8008 || position>0xff88)return false;
    unsigned actor=position-8;
    unsigned owner=ram[actor+12]|(unsigned)ram[actor+13]<<8;
    uint32_t descriptor=ram[actor+4]|(uint32_t)ram[actor+5]<<8|(uint32_t)ram[actor+6]<<16;
    uint32_t action=ram[actor+0x30]|(uint32_t)ram[actor+0x31]<<8|(uint32_t)ram[actor+0x32]<<16;
    uint32_t image=ram[draw+10]|(uint32_t)ram[draw+11]<<8|(uint32_t)ram[draw+12]<<16;
    unsigned x=ram[position]|(unsigned)ram[position+1]<<8;
    unsigned y=ram[position+2]|(unsigned)ram[position+3]<<8;
    /* Displayed OAM is latched before the next actor update. At a phase
     * boundary live draw memory can already hold the following reviewed pose.
     * Keep ownership strict while accepting that observed one-step advance. */
    bool displayed=image==pose || (i+1<sizeof poses/sizeof poses[0] && image==poses[i+1]);
    return owner==draw && displayed && descriptor==0xc5858f && action==0xc55a66 &&
           (ram[draw+9]&0x40) && !(ram[draw+8]&14) && (x==16 || x==226) && y==24;
}
#endif
