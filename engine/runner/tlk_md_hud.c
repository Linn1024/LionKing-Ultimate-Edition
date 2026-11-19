#include "tlk_md_hud.h"
#include <string.h>
enum { START=0x8ec14,END=0x8fdc6 };
static uint8_t data[END-START],meters[2][704];
static int ready,health_max,last[5];
static unsigned lives,adult_portrait;
void TlkMdHudSetAdult(int adult) {adult_portrait=adult!=0;}
static int clamp(int x,int lo,int hi) { return x<lo?lo:x>hi?hi:x; }
static void copy(uint8_t *out,unsigned source) { memcpy(out,data+source-START,64); }
int TlkMdHudInit(const uint8_t *rom,size_t size) {
    ready=0;if (!rom || size!=0x300000) return 0;
    memcpy(data,rom+START,sizeof data);ready=1;
    for (unsigned i=0;i<5;i++) last[i]=-100;
    return 1;
}
int TlkMdHudReady(void) { return ready; }
int TlkMdHudGenerate(unsigned kind,int maximum,int current,uint8_t *out,size_t capacity) {
    if (!ready || kind>1 || !out || capacity<704) return 0;
    maximum=clamp(maximum,kind?4:16,kind?14:48);current=clamp(current,0,maximum);
    int count=clamp(maximum>>(kind?1:3),2,9),remaining=kind?current:current>>2;
    static const unsigned body[2][3]={{0x8ec94,0x8ed54,0x8ee14},{0x8fb06,0x8fbc6,0x8fc86}};
    copy(out,kind?0x8fa86:0x8ec14);unsigned at=64;
    for (int i=0;i<count;i++) {
        unsigned source=body[kind][i%3];
        if (remaining>0) { remaining-=2;source+=(unsigned)(2+(remaining<0?remaining:0))*64; }
        else { remaining--;if (remaining!=-1) source=0x8fac6; }
        copy(out+at,source);at+=64;
    }
    copy(out+at,current==maximum?0x8fd46:0x8fd86);at+=64;
    memset(out+at,0,(size_t)(9-count)*64);return 1;
}
void TlkMdHudPrepare(int roar_max,int roar_current,int maximum,int current,unsigned count) {
    int values[5]={roar_max,roar_current,maximum,current,(int)count};
    if (!ready || !memcmp(last,values,sizeof last)) return;
    TlkMdHudGenerate(0,roar_max,roar_current,meters[0],704);
    TlkMdHudGenerate(1,maximum,current,meters[1],704);
    health_max=clamp(maximum,4,14);lives=count;memcpy(last,values,sizeof last);
}
int TlkMdHudHealthMaximum(void) { return health_max; }
int TlkMdHudLifeReady(void) { return ready && lives<=9; }
static unsigned pixel(const uint8_t *source,unsigned width,unsigned height,int x,int y) {
    if (x<0 || y<0 || x>=(int)width || y>=(int)height) return 0;
    unsigned at=((unsigned)x/8*(height/8)+(unsigned)y/8)*32+(unsigned)(y&7)*4+(unsigned)(x&7)/2;
    return (source[at]>>((x&1)?0:4))&15;
}
unsigned TlkMdHudPixel(unsigned kind,int x,int y) {
    if (!ready || kind>2) return 0;
    if (kind==2) {
        /* Both original portraits are already in the installed HUD payload.
         * Actual MD5/6 VRAM puts these288-byte images in the same tile bank. */
        unsigned color=pixel(data+(adult_portrait?0x8f318:0x8f1f8)-START,24,24,x-6,y+6);
        if (!color && lives<=9) color=pixel(data+0x8f438-START+lives*128,16,16,x-32,y);
        return color;
    }
    /* These are the original three MD pieces, including their overlap. */
    unsigned color=pixel(meters[kind],8,16,x-5,y);
    if (!color) color=pixel(meters[kind]+64,32,16,x-8,y);
    if (!color) color=pixel(meters[kind]+320,32,16,x-40,y);
    return color;
}
