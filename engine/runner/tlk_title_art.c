#include "tlk_title_art.h"
#include "tlk_revival_art.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "sha256.h"

enum { CAPTION_COUNT=15,CAPTION_GLYPHS=64 };
typedef struct CaptionImage {
    unsigned level,hint,count,frame;
    uint16_t glyphs[CAPTION_GLYPHS][3];
    int geometry[4];uint8_t *pixels;
} CaptionImage;
static const unsigned caption_frames[CAPTION_COUNT]={
    0x1d5dac,0x1d5e74,0x1d5f5c,0x1d6064,0x1d60ec,0x1d6184,0x1d620c,
    0x1d6294,0x1d62fc,0x1d6384,0x1d640c,0x1d6484,0x1d64fc,0x1d6574,0x1d5d04};
struct TlkTitleArt {
    TlkRevivalArt *images;uint16_t native[16],md[16];
    int geometry[2][4];uint8_t *pixels[2];
    unsigned caption_count;CaptionImage captions[CAPTION_COUNT];
};
#ifdef TLK_TITLE_ART_PREPARE
#include "tlk_caption_extra_prepare.inc"
TlkTitleArt *TlkTitleArtCreate(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms) {
    TlkRevivalArt *images=TlkRevivalArtCreatePrideTitle(snes,ss,md,ms);if(!images)return NULL;
    TlkTitleArt *art=calloc(1,sizeof *art);
    if(!art){TlkRevivalArtFree(images);return NULL;}art->images=images;
    for(unsigned i=0;i<16;i++) {
        art->native[i]=(uint16_t)(snes[0x7b93+i*2]|(unsigned)snes[0x7b94+i*2]<<8);
        unsigned raw=(unsigned)md[0x1d78aa+i*2]<<8|md[0x1d78ab+i*2];
        unsigned r=raw>>1&7,g=raw>>5&7,b=raw>>9&7;
        art->md[i]=(uint16_t)((r*4+(r>>2))|((g*4+(g>>2))<<5)|((b*4+(b>>2))<<10));
    }
    if(!CaptionCreateExtra(art,snes,ss,md,ms)){TlkTitleArtFree(art);return NULL;}
    return art;
}
#endif
void TlkTitleArtFree(TlkTitleArt *art) {
    if(!art)return;TlkRevivalArtFree(art->images);
    for(unsigned i=0;i<CAPTION_COUNT;i++)free(art->captions[i].pixels);
    free(art->pixels[0]);free(art->pixels[1]);memset(art,0,sizeof *art);free(art);
}
int TlkTitleArtBounds(const TlkTitleArt *art,unsigned source,int *x,int *y,int *w,int *h) {
    if(!art || source>1 || !x || !y || !w || !h)return 0;
    if(art->images)return TlkRevivalArtSourceBounds(art->images,0x7e17dd,source,x,y,w,h);
    if(!art->pixels[source])return 0;
    *x=art->geometry[source][0];*y=art->geometry[source][1];
    *w=art->geometry[source][2];*h=art->geometry[source][3];return 1;
}
static int TitlePixel(const TlkTitleArt *art,int x,int y,unsigned source) {
    if(art->images)return TlkRevivalArtPixel(art->images,0x7e17dd,x,y,source);
    const int *g=art->geometry[source];x-=g[0];y-=g[1];
    return x<0 || y<0 || x>=g[2] || y>=g[3]?0:art->pixels[source][y*g[2]+x];
}
int TlkTitleArtSample(const TlkTitleArt *art,int x,int y,unsigned frames,unsigned palette,
                      const uint16_t cgram[256],uint16_t *color) {
    if(!art || !cgram || !color || frames>1 || palette>1 ||
       memcmp(cgram+129,art->native+1,15*sizeof(uint16_t)))return -1;
    int c=TitlePixel(art,x,y,frames);
    if(c<=0)return c;
    *color=palette?art->md[c]:cgram[128+c];return 1;
}
int TlkTitleArtCaptionsReady(const TlkTitleArt *art){return art && art->caption_count==CAPTION_COUNT;}
static const CaptionImage *CaptionSlot(const TlkTitleArt *art,unsigned slot) {
    return TlkTitleArtCaptionsReady(art) && slot && slot<=CAPTION_COUNT?&art->captions[slot-1]:NULL;
}
unsigned TlkTitleArtCaptionMatch(const TlkTitleArt *art,unsigned level,unsigned hint,
                                const uint8_t *p,size_t size) {
    if(!TlkTitleArtCaptionsReady(art) || !p || level>13 || hint>1 || (hint && level!=1) || size<27)return 0;
    unsigned slot=hint?15:level+1;const CaptionImage *c=CaptionSlot(art,slot);
    unsigned count=p[0]|(unsigned)p[1]<<8;
    if(!c || c->count!=count || count>CAPTION_GLYPHS || size<27+count*6)return 0;
    for(unsigned i=0;i<count;i++) {
        const uint8_t *g=p+27+i*6;
        if((g[0]|(unsigned)g[1]<<8)!=c->glyphs[i][0] ||
           (g[4]|(unsigned)g[5]<<8)!=c->glyphs[i][2])return 0;
    }
    return slot;
}
int TlkTitleArtCaptionBounds(const TlkTitleArt *art,unsigned slot,int *x,int *y,int *w,int *h) {
    const CaptionImage *c=CaptionSlot(art,slot);if(!c || !x || !y || !w || !h)return 0;
    *x=c->geometry[0];*y=c->geometry[1];*w=c->geometry[2];*h=c->geometry[3];return 1;
}
static int CaptionPalette(const TlkTitleArt *art,const uint16_t *native,const uint16_t *cgram) {
    if(!art || !cgram)return 0;
    if(native)return !memcmp(cgram+129,native+1,30);
    /* King cycles bank0 entries8..10 for the scene; neither original caption
     * font uses these indices. Keep the shared text/outline colors guarded. */
    for(unsigned i=1;i<16;i++)if((i<8 || i>10) && cgram[128+i]!=art->native[i])return 0;
    return 1;
}
int TlkTitleArtCaptionSample(const TlkTitleArt *art,unsigned slot,int x,int y,unsigned palette,
                            const uint16_t *native,const uint16_t *cgram,uint16_t *color) {
    const CaptionImage *c=CaptionSlot(art,slot);
    if(!c || !color || palette>1 || !CaptionPalette(art,native,cgram))return -1;
    x-=c->geometry[0];y-=c->geometry[1];
    if(x<0 || y<0 || x>=c->geometry[2] || y>=c->geometry[3])return 0;
    unsigned pixel=c->pixels[y*c->geometry[2]+x];if(!pixel)return 0;
    *color=palette?art->md[pixel]:cgram[128+pixel];return 1;
}
int TlkTitleArtCaptionColor(const TlkTitleArt *art,unsigned slot,unsigned pixel,
                           const uint16_t *native,const uint16_t *cgram,uint16_t *color) {
    if(!CaptionSlot(art,slot) || !color || pixel>15 || !CaptionPalette(art,native,cgram))return -1;
    if(!pixel)return 0;*color=art->md[pixel];return 1;
}
#include "tlk_title_art_assets.inc"
