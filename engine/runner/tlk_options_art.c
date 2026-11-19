#include "tlk_options_art_internal.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>
static uint32_t options_get32(const uint8_t *p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
TlkOptionsArt *TlkOptionsArtLoad(const uint8_t *data,size_t size) {
    static const uint8_t source[32]={0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
    if(!data || size!=OPTIONS_RECORD || memcmp(data,"TLKOPAR1",8) || options_get32(data+8)!=1 ||
       options_get32(data+12)!=112 || options_get32(data+16)!=size || options_get32(data+20)!=96 || memcmp(data+24,source,32))return NULL;
    for(unsigned i=88;i<112;i++)if(data[i])return NULL;
    uint8_t hash[32];sha256_compute(data+112,size-112,hash);if(memcmp(hash,data+56,32))return NULL;
    TlkOptionsArt *art=calloc(1,sizeof *art);if(!art)return NULL;const uint8_t *p=data+112;
    for(unsigned i=0;i<64;i++,p+=2){art->palette[i]=(uint16_t)(p[0]|(unsigned)p[1]<<8);if(art->palette[i]>0x7fff)goto fail;}
    for(unsigned i=0;i<OPTIONS_PIXELS;i++,p++){if(*p>127)goto fail;art->base[i]=*p;}
    for(unsigned i=0;i<96*64;i++,p++){if(*p>15)goto fail;((uint8_t*)art->font)[i]=*p;}
    for(unsigned i=0;i<576;i++,p++){if(*p>15)goto fail;art->selector[i]=*p;}
    for(unsigned i=0;i<6;i++) {
        unsigned seen=0;for(unsigned j=0;j<3;j++,p++){if(*p<'a' || *p>'c' || (seen&(1u<<(*p-'a'))))goto fail;seen|=1u<<(*p-'a');art->buttons[i][j]=*p;}
    }
    return art;
fail:free(art);return NULL;
}
void TlkOptionsArtFree(TlkOptionsArt *art){free(art);}
static void options_text_base(const TlkOptionsArt *art,const uint8_t *base,const char *text,unsigned x,unsigned y,const uint32_t *colors,uint32_t *out) {
    for(;*text;text++,x+=8) {
        unsigned character=(unsigned char)*text;if(character<32 || character>127 || x>312 || y>216)return;
        const uint8_t *glyph=art->font[character-32];
        for(unsigned py=0;py<8;py++)for(unsigned px=0;px<8;px++) {
            unsigned index=glyph[py*8+px],at=(y+py)*320+x+px;
            if(index && !(base[at]&64))out[at]=colors[32+index];
        }
    }
}
static void options_text(const TlkOptionsArt *art,const char *text,unsigned x,unsigned y,const uint32_t *colors,uint32_t *out) {
    options_text_base(art,art->base,text,x,y,colors,out);
}
int TlkOptionsArtDrawDebugMenu(const TlkOptionsArt *art,const uint8_t *base,const uint8_t *names,
    unsigned selected,unsigned bob_x,unsigned invincible,unsigned level,uint32_t *out) {
    if(!art || !base || !names || !out || selected>1 || bob_x<21 || bob_x>31 || invincible>2 || level>=14)return 0;
    uint32_t colors[64];for(unsigned i=0;i<64;i++) {
        unsigned c=art->palette[i];colors[i]=0xff000000u;
        for(unsigned j=0;j<3;j++){unsigned v=(c>>(j*5))&31;colors[i]|=((v<<3)|(v>>2))<<((2-j)*8);}
    }
    for(unsigned i=0;i<OPTIONS_PIXELS;i++)out[i]=colors[base[i]&63];
    options_text_base(art,base,invincible?"yes":"no",152,120,colors,out);
    char name[21];memcpy(name,names+level*20,20);name[20]=0;
    options_text_base(art,base,name,152,128,colors,out);
    for(unsigned y=0;y<24;y++)for(unsigned x=0;x<24;x++) {
        unsigned index=art->selector[y*24+x];if(index)out[(112+selected*8+y)*320+bob_x-11+x]=colors[32+index];
    }
    return 1;
}
int TlkOptionsArtDrawSoundTest(const TlkOptionsArt *art,const uint8_t *base,const uint8_t *catalog,
    unsigned selected,unsigned bob_x,uint32_t *out) {
    if(!art || !base || !catalog || !out || selected>=16 || bob_x<70 || bob_x>80)return 0;
    uint32_t colors[64];for(unsigned i=0;i<64;i++) {
        unsigned c=art->palette[i];colors[i]=0xff000000u;
        for(unsigned j=0;j<3;j++){unsigned v=(c>>(j*5))&31;colors[i]|=((v<<3)|(v>>2))<<((2-j)*8);}
    }
    for(unsigned i=0;i<OPTIONS_PIXELS;i++)out[i]=colors[base[i]&63];
    for(unsigned row=0;row<7;row++) {
        char name[17];memcpy(name,catalog+((selected+row+13)%16)*18+2,16);name[16]=0;
        options_text_base(art,base,name,96,96+row*8,colors,out);
    }
    for(unsigned y=0;y<24;y++)for(unsigned x=0;x<24;x++) {
        unsigned index=art->selector[y*24+x];if(index)out[(112+y)*320+bob_x-11+x]=colors[32+index];
    }
    return 1;
}
int TlkOptionsArtDrawSoundTestRows(const TlkOptionsArt *art,const uint8_t *base,
    const char names[7][21],unsigned bob_x,uint32_t *out) {
    if(!art || !base || !names || !out || bob_x<70 || bob_x>80)return 0;
    uint32_t colors[64];for(unsigned i=0;i<64;i++) {
        unsigned c=art->palette[i];colors[i]=0xff000000u;
        for(unsigned j=0;j<3;j++){unsigned v=(c>>(j*5))&31;colors[i]|=((v<<3)|(v>>2))<<((2-j)*8);}
    }
    for(unsigned i=0;i<OPTIONS_PIXELS;i++)out[i]=colors[base[i]&63];
    for(unsigned row=0;row<7;row++)options_text_base(art,base,names[row],96,96+row*8,colors,out);
    for(unsigned y=0;y<24;y++)for(unsigned x=0;x<24;x++) {
        unsigned index=art->selector[y*24+x];if(index)out[(112+y)*320+bob_x-11+x]=colors[32+index];
    }
    return 1;
}
int TlkOptionsArtDrawBindings(const TlkOptionsArt *art,unsigned selected,unsigned bob_x,
    unsigned difficulty,unsigned music,unsigned effects,const char buttons[3],uint32_t *out) {
    if(!art || !out || !buttons || selected>5 || bob_x<38 || bob_x>48 || difficulty>2 || music>1 || effects>1)return 0;
    for(unsigned i=0;i<3;i++)if((unsigned char)buttons[i]<32 || (unsigned char)buttons[i]>127)return 0;
    uint32_t colors[64];for(unsigned i=0;i<64;i++) {
        unsigned c=art->palette[i];colors[i]=0xff000000u;
        for(unsigned j=0;j<3;j++){unsigned v=(c>>(j*5))&31;colors[i]|=((v<<3)|(v>>2))<<((2-j)*8);}
    }
    for(unsigned i=0;i<OPTIONS_PIXELS;i++)out[i]=colors[art->base[i]&63];
    static const char *difficulties[]={"easy","normal","difficult"};
    options_text(art,difficulties[difficulty],176,80,colors,out);
    options_text(art,music?"yes":"no",176,96,colors,out);options_text(art,effects?"yes":"no",176,112,colors,out);
    for(unsigned i=0;i<3;i++){char text[2]={buttons[i],0};options_text(art,text,224,136+i*8,colors,out);}
    for(unsigned y=0;y<24;y++)for(unsigned x=0;x<24;x++) {
        unsigned index=art->selector[y*24+x];if(index)out[(72+selected*16+y)*320+bob_x-11+x]=colors[32+index];
    }
    return 1;
}
int TlkOptionsArtDraw(const TlkOptionsArt *art,unsigned selected,unsigned bob_x,
    unsigned difficulty,unsigned music,unsigned effects,unsigned configuration,uint32_t *out) {
    if(!art || configuration>5)return 0;
    return TlkOptionsArtDrawBindings(art,selected,bob_x,difficulty,music,effects,(const char*)art->buttons[configuration],out);
}
