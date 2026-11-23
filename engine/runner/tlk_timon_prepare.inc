/* Installer-only scene banks. Native playback never decodes these ROMs. */
#include "sha256.h"
static unsigned timon_le16(const uint8_t *p){return p[0]|(unsigned)p[1]<<8;}
static int timon_trim(Image *f){
    unsigned left=f->w,top=f->h,right=0,bottom=0;
    for(unsigned y=0;y<f->h;y++)for(unsigned x=0;x<f->w;x++)if(f->pixels[y*f->w+x]){
        if(x<left)left=x;if(y<top)top=y;if(x+1>right)right=x+1;if(y+1>bottom)bottom=y+1;
    }
    if(right<=left || bottom<=top)return 0;
    unsigned w=right-left,h=bottom-top;uint8_t *p=malloc(w*h);if(!p)return 0;
    for(unsigned y=0;y<h;y++)memcpy(p+y*w,f->pixels+(y+top)*f->w+left,w);
    free(f->pixels);f->pixels=p;f->x+=(int)left;f->y+=(int)top;f->w=w;f->h=h;return 1;
}
static int timon_native_image(const uint8_t *rom,const uint8_t *bank,size_t size,unsigned source,Image *out){
    unsigned flags=timon_le16(rom+source),large=flags&127,count=large;
    if((flags&0x8000) || !large || large>32 || rom[source+26]!=0x7f)return 0;
    unsigned end=source+27+count*6;
    if(flags&0x4000){while(end<0x300000-6 && timon_le16(rom+end)!=0xaaaa && count<64){count++;end+=6;}if(timon_le16(rom+end)!=0xaaaa)return 0;}
    Piece pieces[64];int left=512,top=512,right=-512,bottom=-512;
    for(unsigned i=0;i<count;i++){
        const uint8_t *p=rom+source+27+i*6;Piece *q=pieces+i;
        q->x=signed16(timon_le16(p));q->y=signed16(timon_le16(p+2));q->source=timon_le16(p+4);q->w=q->h=i<large?16:8;
        if(q->x<-256 || q->x>256 || q->y<-224 || q->y>224 || q->source>size || q->w*q->h/2>size-q->source)return 0;
        if(q->x<left)left=q->x;if(q->y<top)top=q->y;
        if(q->x+(int)q->w>right)right=q->x+q->w;if(q->y+(int)q->h>bottom)bottom=q->y+q->h;
    }
    if(right<=left || bottom<=top || right-left>256 || bottom-top>224)return 0;
    out->source=source|0xc00000;out->x=left;out->y=top;out->w=right-left;out->h=bottom-top;out->pixels=calloc(out->w*out->h,1);if(!out->pixels)return 0;
    for(unsigned n=count;n;n--){const Piece *q=pieces+n-1;
        for(unsigned y=0;y<q->h;y++)for(unsigned x=0;x<q->w;x++){
            unsigned at=q->source+((y/8)*2+x/8)*32+(y&7)*2,bit=7-(x&7),v=0;
            for(unsigned plane=0;plane<4;plane++)v|=((bank[at+(plane&1)+(plane>=2?16:0)]>>bit)&1)<<plane;
            if(v)out->pixels[(q->y-top+(int)y)*out->w+q->x-left+(int)x]=(uint8_t)v;
        }
    }
    return timon_trim(out);
}
static int prepare_timon(const uint8_t *s,const uint8_t *m,uint8_t **result,size_t *bytes){
    *result=NULL;*bytes=0;uint8_t *nb=malloc(65536),*mb=malloc(65536),*data=NULL;size_t ns=0,ms=0,total=128+22*48;Image images[22][2]={0};int ok=0;
    if(!nb || !mb || !TlkMdDecompress(s,0x300000,0x160001,nb,65536,&ns) || ns!=31744 ||
       !TlkMdDecompress(m,0x300000,0x1d7a2c,mb,65536,&ms) || ms!=31008)goto done;
    for(unsigned i=0;i<22;i++){
        unsigned a=0x25d52+i*4,b=0x1d7950+i*4;
        unsigned np=s[a+1]|(unsigned)s[a+2]<<8|(unsigned)s[a+3]<<16,mp=be32(m+b)&0xffffff;
        if(s[a]>=253 || m[b]!=3 || np<0xc1da38 || np>0xc1e545 || mp<0x1dadca || mp>0x1ddfb2 ||
           !timon_native_image(s,nb,ns,np&0x3fffff,&images[i][0]) ||
           !image_decode(m,mb,ms,mp,&images[i][1]) || !timon_trim(&images[i][1]))goto done;
        for(unsigned j=0;j<2;j++)total+=images[i][j].w*images[i][j].h;
    }
    if(s[0x25daa]!=255 || m[0x1d79a8]!=255)goto done;
    data=calloc(1,total);if(!data)goto done;memcpy(data,"TLKTMN01",8);TlkDataPut32(data+8,1);TlkDataPut32(data+12,(uint32_t)total);TlkDataPut32(data+16,22);TlkDataPut32(data+20,(uint32_t)ns);sha256_compute(nb,ns,data+24);
    for(unsigned i=0;i<16;i++){TlkDataPut16(data+56+i*2,(uint16_t)timon_le16(s+0x746a+i*2));TlkDataPut16(data+88+i*2,TlkMdColor555(be16(m+0x1d79ac+i*2)));}
    size_t at=128+22*48;
    for(unsigned i=0;i<22;i++){
        uint8_t *p=data+128+i*48;TlkDataPut32(p,images[i][0].source);TlkDataPut32(p+4,images[i][1].source);TlkDataPut32(p+8,s[0x25d52+i*4]+1);TlkDataPut32(p+12,4);
        for(unsigned j=0;j<2;j++){
            const Image *f=&images[i][j];unsigned n=f->w*f->h;uint8_t *desc=p+16+j*8;
            TlkDataPut16(desc,(uint16_t)f->x);TlkDataPut16(desc+2,(uint16_t)f->y);TlkDataPut16(desc+4,(uint16_t)f->w);TlkDataPut16(desc+6,(uint16_t)f->h);
            TlkDataPut32(p+32+j*4,(uint32_t)at);TlkDataPut32(p+40+j*4,n);memcpy(data+at,f->pixels,n);at+=n;
        }
    }
    if(at!=total)goto done;*result=data;*bytes=total;data=NULL;ok=1;
done:for(unsigned i=0;i<22;i++)for(unsigned j=0;j<2;j++)free(images[i][j].pixels);free(nb);free(mb);free(data);return ok;
}
