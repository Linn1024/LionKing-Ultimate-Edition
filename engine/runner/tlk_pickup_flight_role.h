#ifndef TLK_PICKUP_FLIGHT_ROLE_H
#define TLK_PICKUP_FLIGHT_ROLE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* The two shared pickup flights. Pose identity alone must not
 * admit unrelated fixed-screen artwork. The caller owns displayed OAM and
 * still applies the normal palette/flash checks when sampling artwork. */
static inline bool TlkPickupFlightCommonDrawRole(const uint8_t *ram,size_t size,
                                                unsigned draw,uint32_t pose,bool fixed) {
    if(!fixed || !ram || size<0x20000 || draw<0x8000 || draw>0xffe8 ||
       (pose!=0xc528bc && pose!=0xc528dd))return false;
    unsigned position=ram[draw+4]|(unsigned)ram[draw+5]<<8;
    if(position<0x8008 || position>0xff88)return false;
    unsigned actor=position-8;
    unsigned owner=ram[actor+12]|(unsigned)ram[actor+13]<<8;
    uint32_t descriptor=ram[actor+4]|(uint32_t)ram[actor+5]<<8|(uint32_t)ram[actor+6]<<16;
    uint32_t action=ram[actor+0x30]|(uint32_t)ram[actor+0x31]<<8|(uint32_t)ram[actor+0x32]<<16;
    uint32_t image=ram[draw+10]|(uint32_t)ram[draw+11]<<8|(uint32_t)ram[draw+12]<<16;
    if(owner!=draw || image!=pose || !(ram[draw+9]&0x40) || (ram[draw+8]&14))return false;
    return pose==0xc528bc ? descriptor==0xc58945 && action==0xc55247 :
                            descriptor==0xc58951 && action==0xc55413;
}

/* Preserve the reviewed Pride-only movement/viewport adapter. */
static inline bool TlkPickupFlightDrawRole(const uint8_t *ram,size_t size,
                                          unsigned draw,uint32_t pose,bool fixed) {
    if(!ram || size<0x20000)return false;
    unsigned level=ram[0x1ff9e]|(unsigned)ram[0x1ff9f]<<8;
    uint32_t scene=ram[0xdf]|(uint32_t)ram[0xe0]<<8|(uint32_t)ram[0xe1]<<16;
    return !level && (scene==0xc00387 || scene==0xc0080d) &&
        !ram[0x2000] && !ram[0x2001] &&
        TlkPickupFlightCommonDrawRole(ram,size,draw,pose,fixed);
}
#endif
