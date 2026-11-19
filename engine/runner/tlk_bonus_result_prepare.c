/* Installer translation of the original normal bonus result card. */
#include "tlk_bonus_result_data.h"
#include "tlk_data_record.h"
#include "tlk_md_assets.h"
#include <stdlib.h>
#include <string.h>
enum { LABEL_AT=224,DIGITS_AT=LABEL_AT+320*224,FONT_AT=DIGITS_AT+10*16*18,
       SAMPLE_AT=FONT_AT+36*256,TOTAL=SAMPLE_AT+0x51c3 };
static unsigned be16(const uint8_t *p){return (unsigned)p[0]<<8|p[1];}
static unsigned be32(const uint8_t *p){return be16(p)<<16|be16(p+2);}
static int signed16(unsigned v){return v<32768?(int)v:(int)v-65536;}
static int md_frame(const uint8_t *m,unsigned source,int ox,int oy,unsigned width,unsigned height,uint8_t *out){
    if(source>0x300000-24)return 0;unsigned count=be16(m+source)+1,bytes=0;
    if(count>32 || source+24+count*16>0x300000)return 0;
    for(unsigned remaining=count;remaining;remaining--){
        const uint8_t *q=m+source+24+(remaining-1)*16;
        unsigned w=be16(q),h=be16(q+2),at=be32(q+12);int dx=signed16(be16(q+4))+ox,dy=signed16(be16(q+6))+oy;
        if(!w || w>32 || (w&7) || !h || h>32 || (h&7) || at>0x300000 || w*h/2>0x300000-at ||
           be16(q+8)!=(((w/8-1)*4+h/8-1)<<8))return 0;
        bytes+=w*h/2;
        for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
            unsigned a=at+((x/8)*(h/8)+y/8)*32+(y&7)*4+(x&7)/2;
            unsigned v=(m[a]>>((x&1)?0:4))&15;int xx=dx+x,yy=dy+y;
            if(v && xx>=0 && xx<(int)width && yy>=0 && yy<(int)height)out[yy*width+xx]=v;
        }
    }
    return bytes==be16(m+source+10);
}
int TlkBonusResultDataPrepare(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    if(!s || !m || sn!=0x300000 || mn!=0x300000 || memcmp(s+0x3b88b,"00 BUGS CAUGHT",14) ||
       be32(m+0x1cdfa6)!=0x0c790014 || be16(m+0x1ce042)!=0x3e3c || be16(m+0x1ce060)!=0x0c47 ||
       be16(m+0x1ce014)!=0x0c46 || be16(m+0x1ce016)!=99 || be32(m+0x1ce082)!=0x1d67b0 ||
       be32(m+0x1ce088)!=0x1cec48)return 0;
    uint8_t *p=calloc(TOTAL,1);if(!p)return 0;memcpy(p,"TLKBR001",8);
    unsigned header[]={1,TOTAL,LABEL_AT,DIGITS_AT,FONT_AT,SAMPLE_AT,0x51c3,113,40,8,25,150,120,20};
    for(unsigned i=0;i<14;i++)TlkDataPut32(p+8+i*4,header[i]);
    for(unsigned i=0;i<64;i++)TlkDataPut16(p+64+i*2,TlkMdColor555(be16(m+0x212a26+i*2)));
    for(unsigned i=0;i<16;i++)TlkDataPut16(p+192+i*2,TlkDataGet16(s+0x7c93+i*2));
    int ok=md_frame(m,0x1cec48,-48,32,320,224,p+LABEL_AT);
    for(unsigned i=0;i<10 && ok;i++)ok=md_frame(m,be32(m+0x1cee60+i*4),0,0,16,18,p+DIGITS_AT+i*16*18);
    for(unsigned glyph=0;glyph<36;glyph++)for(unsigned y=0;y<16;y++)for(unsigned x=0;x<16;x++){
        unsigned a=0x2888ef+glyph*128+(y/8*2+x/8)*32+(y&7)*2,bit=7-(x&7),v=0;
        for(unsigned plane=0;plane<4;plane++)v|=((s[a+(plane&1)+(plane>=2?16:0)]>>bit)&1)<<plane;
        p[FONT_AT+glyph*256+y*16+x]=v;
    }
    memcpy(p+SAMPLE_AT,m+0x2f2d6a,0x51c3);
    if(ok)ok=TlkBonusResultDataRead(p,TOTAL,1);free(p);return ok;
}
