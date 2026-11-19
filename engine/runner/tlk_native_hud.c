#include "tlk_native_hud.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

enum { FONT_START=0x405ff,FONT_SIZE=0x620,READY=0x54484e31 };
struct TlkNativeHud { unsigned ready;uint8_t font[FONT_SIZE]; };
#ifdef TLK_NATIVE_HUD_PREPARE
TlkNativeHud *TlkNativeHudCreate(const uint8_t *rom,size_t size) {
    static const uint8_t expected[32]={0x45,0x7a,0xbe,0x63,0x4e,0x0a,0x8b,0xe0,0x3e,0x29,0x51,0x3a,0x3d,0xca,0x8f,0x3e,
        0x9d,0x0d,0xdc,0x6b,0xf9,0x7d,0x89,0x31,0xf2,0x31,0x60,0x94,0x26,0x0f,0x37,0x12};
    if(!rom || size!=0x300000)return NULL;
    uint8_t hash[32];sha256_compute(rom,size,hash);if(memcmp(hash,expected,32))return NULL;
    TlkNativeHud *hud=malloc(sizeof *hud);if(!hud)return NULL;
    memcpy(hud->font,rom+FONT_START,FONT_SIZE);hud->ready=READY;return hud;
}
#endif
TlkNativeHud *TlkNativeHudClone(const TlkNativeHud *hud) {
    if(!hud || hud->ready!=READY)return NULL;
    TlkNativeHud *copy=malloc(sizeof *copy);if(copy)*copy=*hud;return copy;
}
void TlkNativeHudFree(TlkNativeHud *hud) { if(hud) { memset(hud,0,sizeof *hud);free(hud); } }
static void block(const TlkNativeHud *hud,uint8_t *out,unsigned at,unsigned source) {
    unsigned offset=source-0x5ff;
    memcpy(out+at,hud->font+offset,32);memcpy(out+at+256,hud->font+offset+512,32);
}
int TlkNativeHudRestored(const TlkNativeHud *hud,unsigned kind,unsigned maximum,const uint8_t previous[512],uint8_t out[512]) {
    if(!hud || hud->ready!=READY || !previous || !out || kind>1 ||
       (kind==TLK_NATIVE_HUD_HEALTH?(maximum<4 || maximum>12):(maximum<8 || maximum>64)))return 0;
    uint8_t candidate[512];memcpy(candidate,previous,sizeof candidate);
    unsigned count=kind==TLK_NATIVE_HUD_HEALTH?maximum/2:maximum/8;
    if(count>6)count=6;
    unsigned at=32,pattern=0;
    for(unsigned n=0;n<count;n++) {
        unsigned glyph=(kind==TLK_NATIVE_HUD_HEALTH?11:4)+pattern;
        block(hud,candidate,at,0x5ff+glyph*32);at+=32;pattern=(pattern+2)%6;
    }
    /* Both full-value loops leave their previous-full flag nonzero. */
    block(hud,candidate,at,0x71f);at+=32;
    unsigned test=at+(kind==TLK_NATIVE_HUD_HEALTH?0:8);
    if(at<256 && (candidate[test] || candidate[test+1])) {
        memset(candidate+at,0,256-at);memset(candidate+at+256,0,256-at);
    }
    memcpy(out,candidate,sizeof candidate);return 1;
}
int TlkNativeHudRoarCurrent(const TlkNativeHud *hud,unsigned maximum,unsigned current,
                           uint16_t initial_full,const uint8_t previous[512],uint8_t out[512]) {
    if(!hud || hud->ready!=READY || !previous || !out || maximum<8 || maximum>64 || current>maximum)return 0;
    uint8_t candidate[512];memcpy(candidate,previous,sizeof candidate);
    unsigned count=maximum/8;if(count>6)count=6;
    unsigned at=32,pattern=0,remaining=current;
    uint16_t full=initial_full;
    for(unsigned n=0;n<count;n++) {
        unsigned glyph;
        if(remaining>=8) { remaining-=8;glyph=4+pattern;full=(uint16_t)(full+1); }
        else if(remaining>=4) { remaining=0;glyph=3+pattern;full=0; }
        else { remaining=0;glyph=full?2:1;full=0; }
        block(hud,candidate,at,0x5ff+glyph*32);at+=32;pattern=(pattern+2)%6;
    }
    block(hud,candidate,at,full?0x71f:0x9ff);at+=32;
    if(at<256 && (candidate[at+8] || candidate[at+9])) {
        memset(candidate+at,0,256-at);memset(candidate+at+256,0,256-at);
    }
    memcpy(out,candidate,sizeof candidate);return 1;
}
#include "tlk_native_hud_assets.inc"
