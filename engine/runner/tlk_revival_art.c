#include "tlk_revival_art.h"
#include "tlk_death_scene.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "sha256.h"

enum { FRAMES=TLK_REVIVAL_TOKENS+1,PIECES=128 };
typedef struct Piece { int x,y;unsigned w,h,source,stride; } Piece;
typedef struct Image { int x,y,w,h;uint8_t *pixels; } Image;
typedef struct Frame { uint32_t pose;Image image[2]; } Frame;
struct TlkRevivalArt { unsigned count;Frame frames[FRAMES]; };
#if defined(TLK_REVIVAL_ART_PREPARE) || defined(TLK_TITLE_ART_PREPARE) || defined(TLK_CHECKPOINT_ART_PREPARE)
static unsigned le16(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8; }
static unsigned be16(const uint8_t *p) { return (unsigned)p[0]<<8|p[1]; }
static unsigned be32(const uint8_t *p) { return be16(p)<<16|be16(p+2); }
static int signed16(unsigned v) { return v<32768?(int)v:(int)v-65536; }
static int bounds(size_t size,unsigned at,unsigned count) { return at<=size && count<=size-at; }
static int position(Piece *p,unsigned x,unsigned y) {
    p->x=signed16(x);p->y=signed16(y);
    return p->x>=-192 && p->x<=192 && p->y>=-192 && p->y<=192;
}
static unsigned native_pieces(const uint8_t *r,size_t size,unsigned at,Piece *p) {
    at&=0x3fffff;if(!bounds(size,at,29))return 0;
    unsigned flags=le16(r+at),slots=flags&127,q=at+29,count=0,units=0;
    if(!slots || slots>32)return 0;
    if(flags&0x8000) {
        unsigned large=flags&0x4000?(flags>>8)&63:slots;
        unsigned source=(le16(r+at+26)|(unsigned)r[at+28]<<16)&0x3fffff;
        if(large>slots || !bounds(size,source,slots*128))return 0;
        for(unsigned i=0;i<large;i++) {
            if(!bounds(size,q,4) || !position(&p[count],le16(r+q),le16(r+q+2)))return 0;
            p[count].w=p[count].h=16;p[count].source=source+i*64;p[count++].stride=slots*64;q+=4;
        }
        units=large*4;
        if(flags&0x4000) {
            while(bounds(size,q,2) && le16(r+q)!=0xaaaa && units<slots*4) {
                if(count==PIECES || !bounds(size,q,4) || !position(&p[count],le16(r+q),le16(r+q+2)))return 0;
                p[count].w=p[count].h=8;
                p[count].source=source+units/4*64+units%2*32+(units%4/2)*slots*64;
                p[count++].stride=32;units++;q+=4;
            }
            if(!bounds(size,q,2) || le16(r+q)!=0xaaaa)return 0;
        }
    } else {
        if(r[at+26]<0xc0)return 0;
        unsigned bank=(r[at+26]&63)<<16;q=at+27;
        do {
            if(count==PIECES || !bounds(size,q,6) || !position(&p[count],le16(r+q),le16(r+q+2)))return 0;
            unsigned width=count<slots?16:8,source=bank|le16(r+q+4);
            if(!bounds(size,source,width*width/2))return 0;
            p[count].w=p[count].h=width;p[count].source=source;p[count++].stride=width*4;
            units+=width*width/64;q+=6;
            if(count>=slots && !(flags&0x4000))break;
        } while(count<slots || (bounds(size,q,2) && le16(r+q)!=0xaaaa));
        if((flags&0x4000) && (!bounds(size,q,2) || le16(r+q)!=0xaaaa))return 0;
    }
    return units*16==le16(r+at+10)?count:0;
}
static unsigned md_pieces_origin(const uint8_t *r,size_t size,unsigned at,Piece *p,unsigned ox,unsigned oy) {
    if(!bounds(size,at,24))return 0;
    unsigned count=be16(r+at)+1,total=0;if(!count || count>32 || !bounds(size,at+24,count*16))return 0;
    for(unsigned i=0;i<count;i++) {
        unsigned q=at+24+i*16,w=be16(r+q),h=be16(r+q+2),source=be32(r+q+12);
        if(!w || !h || w>32 || h>32 || (w&7) || (h&7) || !bounds(size,source,w*h/2) ||
           !position(&p[i],(be16(r+q+4)-ox)&65535,(be16(r+q+6)-oy)&65535) ||
           be16(r+q+8)>>8!=((w/8-1)<<2|(h/8-1)))return 0;
        p[i].w=w;p[i].h=h;p[i].source=source;p[i].stride=0;total+=w*h/2;
    }
    return total==be16(r+at+10)?count:0;
}
static unsigned pixel(const uint8_t *r,const Piece *p,unsigned x,unsigned y,unsigned md) {
    if(md) {
        unsigned at=p->source+(x/8*(p->h/8)+y/8)*32+(y&7)*4+(x&7)/2;
        return (r[at]>>((x&1)?0:4))&15;
    }
    unsigned at=p->source+x/8*32+y/8*p->stride+(y&7)*2,c=0;
    for(unsigned plane=0;plane<4;plane++)c|=((r[at+(plane&1)+(plane>=2?16:0)]>>(7-(x&7)))&1)<<plane;
    return c;
}
static int render(Image *out,const uint8_t *r,const Piece *p,unsigned count,unsigned md) {
    if(!count)return 0;
    int x0=10000,y0=10000,x1=-10000,y1=-10000;
    for(unsigned i=0;i<count;i++)for(unsigned y=0;y<p[i].h;y++)for(unsigned x=0;x<p[i].w;x++) {
        if(!pixel(r,&p[i],x,y,md))continue;
        int px=p[i].x+(int)x,py=p[i].y+(int)y;
        if(px<x0)x0=px;
        if(py<y0)y0=py;
        if(px>x1)x1=px;
        if(py>y1)y1=py;
    }
    if(x1<x0 || y1<y0 || x1-x0>=256 || y1-y0>=256)return 0;
    Image im={.x=x0,.y=y0,.w=x1-x0+1,.h=y1-y0+1};
    im.pixels=calloc((size_t)im.w*im.h,1);if(!im.pixels)return 0;
    for(unsigned n=count;n;n--) {
        const Piece *piece=&p[n-1];
        for(unsigned y=0;y<piece->h;y++)for(unsigned x=0;x<piece->w;x++) {
            unsigned c=pixel(r,piece,x,y,md);if(!c)continue;
            int ix=piece->x+(int)x-im.x,iy=piece->y+(int)y-im.y;
            im.pixels[iy*im.w+ix]=(uint8_t)c;
        }
    }
    *out=im;return 1;
}
static int decode(Image *out,const uint8_t *r,size_t size,unsigned pose,unsigned md) {
    Piece p[PIECES]={0};unsigned count=md?md_pieces_origin(r,size,pose,p,0,0):native_pieces(r,size,pose,p);
    return render(out,r,p,count,md);
}
#endif
void TlkRevivalArtFree(TlkRevivalArt *art) {
    if(!art)return;
    for(unsigned i=0;i<FRAMES;i++)for(unsigned j=0;j<2;j++)free(art->frames[i].image[j].pixels);
    free(art);
}
#if defined(TLK_REVIVAL_ART_PREPARE) || defined(TLK_TITLE_ART_PREPARE) || defined(TLK_CHECKPOINT_ART_PREPARE)
TlkRevivalArt *TlkRevivalArtCreate(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms) {
    TlkDeathProgram program;
    if(!TlkDeathProgramInit(&program,snes,ss,md,ms))return NULL;
    TlkRevivalArt *art=calloc(1,sizeof *art);if(!art)return NULL;
    art->count=FRAMES;
    for(unsigned i=0;i<FRAMES;i++) {
        const TlkDeathToken *t=i<TLK_REVIVAL_TOKENS?&program.revival[i]:&program.idle;
        Frame *f=&art->frames[i];f->pose=t->snes_pose;
        if(!decode(&f->image[0],snes,ss,t->snes_pose,0) || !decode(&f->image[1],md,ms,t->md_pose,1))goto fail;
        const Image *a=&f->image[0],*b=&f->image[1];
        if(a->x!=b->x || a->y!=b->y || a->w!=b->w || a->h!=b->h || memcmp(a->pixels,b->pixels,(size_t)a->w*a->h))goto fail;
    }
    return art;
fail:
    TlkRevivalArtFree(art);return NULL;
}
TlkRevivalArt *TlkRevivalArtCreateCheckpoint(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms) {
    TlkDeathProgram program;
    if(!TlkDeathProgramInit(&program,snes,ss,md,ms))return NULL;
    static const uint32_t pairs[][2]={{0xc456de,0x973b6},{0xc2fde1,0x977c6},{0xc2fe18,0x977fe}};
    TlkRevivalArt *art=calloc(1,sizeof *art);if(!art)return NULL;
    art->count=sizeof pairs/sizeof *pairs;
    for(unsigned i=0;i<art->count;i++) {
        Frame *f=&art->frames[i];f->pose=pairs[i][0];
        if(!decode(&f->image[0],snes,ss,pairs[i][0],0) || !decode(&f->image[1],md,ms,pairs[i][1],1))goto fail;
        const Image *a=&f->image[0],*b=&f->image[1];
        if(a->x!=b->x || a->y!=b->y || a->w!=b->w || a->h!=b->h || memcmp(a->pixels,b->pixels,(size_t)a->w*a->h))goto fail;
    }
    return art;
fail:
    TlkRevivalArtFree(art);return NULL;
}
TlkRevivalArt *TlkRevivalArtCreatePrideTitle(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms) {
    TlkDeathProgram program;
    if(!TlkDeathProgramInit(&program,snes,ss,md,ms) ||
       memcmp(snes+0x3bc97,"THE PRIDELANDS\r",15) || be32(md+0x1d663a)!=0x1d5dac ||
       be16(md+0x1d5dac)!=10 || be16(md+0x1d5db2)!=208 || be16(md+0x1d5db4)!=17)return NULL;
    TlkRevivalArt *art=calloc(1,sizeof *art);if(!art)return NULL;
    art->count=1;Frame *f=&art->frames[0];f->pose=0x7e17dd;
    Piece p[PIECES]={0};unsigned count=0;
    for(unsigned i=0;i<14;i++) {
        unsigned c=snes[0x3bc97+i];if(c==' ')continue;
        if(c<'A' || c>'Z')goto fail;
        unsigned source=0x2888ef+(c-'A')*128;if(!bounds(ss,source,128))goto fail;
        p[count++]=(Piece){.x=(int)i*16-112,.y=0,.w=16,.h=16,.source=source,.stride=64};
    }
    if(count!=13)goto fail;
    if(!render(&f->image[0],snes,p,count,0))goto fail;
    count=md_pieces_origin(md,ms,0x1d5dac,p,160,72);
    if(count!=11 || !render(&f->image[1],md,p,count,1))goto fail;
    return art;
fail:
    TlkRevivalArtFree(art);return NULL;
}
int TlkRevivalArtDecodeMdCaption(const uint8_t *md,size_t size,unsigned frame,int geometry[4],uint8_t **pixels) {
    if(!md || !geometry || !pixels)return 0;*pixels=NULL;
    Piece pieces[PIECES]={0};Image image={0};
    unsigned count=md_pieces_origin(md,size,frame,pieces,160,72);
    if(!render(&image,md,pieces,count,1))return 0;
    geometry[0]=image.x;geometry[1]=image.y;geometry[2]=image.w;geometry[3]=image.h;
    *pixels=image.pixels;return 1;
}
#endif
unsigned TlkRevivalArtCount(const TlkRevivalArt *art) { return art?art->count:0; }
static const Frame *find(const TlkRevivalArt *art,uint32_t pose) {
    if(art)for(unsigned i=0;i<art->count;i++)if(art->frames[i].pose==pose)return &art->frames[i];
    return NULL;
}
int TlkRevivalArtBounds(const TlkRevivalArt *art,uint32_t pose,int *x,int *y,int *w,int *h) {
    return TlkRevivalArtSourceBounds(art,pose,0,x,y,w,h);
}
int TlkRevivalArtSourceBounds(const TlkRevivalArt *art,uint32_t pose,unsigned source,int *x,int *y,int *w,int *h) {
    const Frame *f=find(art,pose);if(!f || !x || !y || !w || !h)return 0;
    if(source>1)return 0;
    const Image *im=&f->image[source];*x=im->x;*y=im->y;*w=im->w;*h=im->h;return 1;
}
int TlkRevivalArtPixel(const TlkRevivalArt *art,uint32_t pose,int x,int y,unsigned source) {
    const Frame *f=find(art,pose);if(!f || source>1)return -1;
    const Image *im=&f->image[source];
    if(x<im->x || y<im->y || x>=im->x+im->w || y>=im->y+im->h)return 0;
    return im->pixels[(y-im->y)*im->w+x-im->x];
}
#include "tlk_revival_art_assets.inc"
