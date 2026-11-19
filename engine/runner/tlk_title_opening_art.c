#include "tlk_title_opening_art.h"
#include <stdlib.h>
#include <string.h>
enum { HEADER=168,PIXELS=320*224,FRAMES=14 };
typedef struct OpeningFrame { unsigned frame,ticks;int x,y,w,h;uint8_t *pixels; } OpeningFrame;
struct TlkTitleOpeningArt { uint32_t colors[64];uint8_t base[PIXELS];OpeningFrame frames[FRAMES+1]; };
static unsigned u32(const uint8_t *p){return p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static int coordinate(unsigned v,int *out){int64_t n=v<=0x7fffffffu?v:(int64_t)v-0x100000000ll;if(n< -320||n>320)return 0;*out=(int)n;return 1;}
void TlkTitleOpeningArtFree(TlkTitleOpeningArt *a){if(a){for(unsigned i=0;i<=FRAMES;i++)free(a->frames[i].pixels);free(a);}}
TlkTitleOpeningArt *TlkTitleOpeningArtLoad(const uint8_t *p,size_t n){
 if(!p||n<HEADER+PIXELS||n>1024*1024||memcmp(p,"TLKTIO01",8)||u32(p+8)!=2||u32(p+12)!=n||u32(p+16)!=320||u32(p+20)!=224||u32(p+24)!=FRAMES||u32(p+28)!=2||u32(p+160)!=PIXELS||u32(p+164))return NULL;
 TlkTitleOpeningArt *a=calloc(1,sizeof *a);if(!a)return NULL;
 for(unsigned i=0;i<64;i++){unsigned c=p[32+i*2]|(unsigned)p[33+i*2]<<8;if(c>32767)goto fail;a->colors[i]=0xff000000u;for(unsigned j=0;j<3;j++){unsigned v=c>>(j*5)&31;a->colors[i]|=((v<<3)|(v>>2))<<((2-j)*8);}}
 for(unsigned i=0;i<PIXELS;i++){if(p[HEADER+i]>127)goto fail;a->base[i]=p[HEADER+i];}
 const uint8_t *end=p+n;p+=HEADER+PIXELS;
 for(unsigned i=0;i<=FRAMES;i++){
  if((size_t)(end-p)<24)goto fail;OpeningFrame *f=a->frames+i;f->frame=u32(p);f->ticks=u32(p+4);unsigned w=u32(p+16),h=u32(p+20);
  if((i<FRAMES?(f->frame<0x29f252||f->frame>0x29f5ea):f->frame!=0x290c62)||(f->frame&1)||!f->ticks||f->ticks>256||!coordinate(u32(p+8),&f->x)||!coordinate(u32(p+12),&f->y)||!w||w>320||!h||h>128||(size_t)w*h>(size_t)(end-p-24))goto fail;
  f->w=w;f->h=h;p+=24;size_t bytes=(size_t)w*h;for(size_t j=0;j<bytes;j++)if(p[j]>15)goto fail;
  f->pixels=malloc(bytes);if(!f->pixels)goto fail;memcpy(f->pixels,p,bytes);p+=bytes;
 }
 if(p!=end)goto fail;return a;
fail:TlkTitleOpeningArtFree(a);return NULL;
}
int TlkTitleOpeningArtBackdrop(const TlkTitleOpeningArt *a,uint32_t *out){
 if(!a||!out)return 0;for(unsigned i=0;i<PIXELS;i++)out[i]=a->colors[a->base[i]&63];return 1;
}
int TlkTitleOpeningArtDraw(const TlkTitleOpeningArt *a,unsigned age,uint32_t *out){
 if(!TlkTitleOpeningArtBackdrop(a,out))return 0;const OpeningFrame *logo=a->frames+FRAMES;
 for(int y=0;y<logo->h;y++)for(int x=0;x<logo->w;x++){int dx=x+logo->x,dy=y+logo->y-16;unsigned c=logo->pixels[y*logo->w+x];if(c&&dx>=0&&dx<320&&dy>=0&&dy<224)out[dy*320+dx]=a->colors[32+c];}
 if(age<2)return 1;
 age-=2;unsigned n=0;while(n+1<FRAMES&&age>=a->frames[n].ticks){age-=a->frames[n].ticks;n++;}
 const OpeningFrame *f=a->frames+n;
 for(int y=0;y<f->h;y++)for(int x=0;x<f->w;x++){int dx=x+f->x,dy=y+f->y+32;unsigned c=f->pixels[y*f->w+x];if(c&&dx>=0&&dx<320&&dy>=0&&dy<224)out[dy*320+dx]=a->colors[48+c];}
 return 1;
}
