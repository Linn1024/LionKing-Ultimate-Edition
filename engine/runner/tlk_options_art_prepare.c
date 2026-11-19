#include "tlk_options_art_internal.h"
#include "tlk_options_art_prepare.h"
#include "tlk_md_assets.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>
static unsigned op_be16(const uint8_t *p){return (unsigned)p[0]<<8|p[1];}
static uint32_t op_be32(const uint8_t *p){return (uint32_t)op_be16(p)<<16|op_be16(p+2);}
static void op_put32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(i*8));}
static int op_signed(unsigned v){return v&0x8000?(int)v-65536:(int)v;}
static int op_span(size_t size,unsigned at,size_t length){return at<=size && length<=size-at;}
static void op_plane(uint8_t *canvas,const uint8_t *map,const uint8_t *tiles,unsigned priority){
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<320;x++) {
        unsigned cell=op_be16(map+((y/8)*64+x/8)*2);if((cell>>15)!=priority)continue;
        unsigned px=(cell&0x800)?7-(x&7):(x&7),py=(cell&0x1000)?7-(y&7):(y&7);
        unsigned index=(tiles[(cell&2047)*32+py*4+px/2]>>((px&1)?0:4))&15;
        if(index)canvas[y*320+x]=(uint8_t)(((cell>>9)&48)|index|(priority?64:0));
    }
}
static int op_frame(uint8_t *canvas,const uint8_t *rom,size_t size,const uint8_t *ram,unsigned frame,int x,int y,unsigned bank) {
    if(!op_span(size,frame,24))return 0;unsigned count=op_be16(rom+frame)+1,total=0;
    if(!count || count>80 || !op_span(size,frame+24,count*16))return 0;
    for(unsigned remaining=count;remaining;remaining--) {
        const uint8_t *p=rom+frame+24+(remaining-1)*16;
        unsigned w=op_be16(p),h=op_be16(p+2),flags=op_be16(p+8);int dx=op_signed(op_be16(p+4)),dy=op_signed(op_be16(p+6));
        uint32_t source=op_be32(p+12);if((source>>24)!=0 && (source>>24)!=255)return 0;source&=0xffffff;
        if(!w || w>32 || (w&7) || !h || h>32 || (h&7) || flags!=(((w/8-1)<<2)|(h/8-1))<<8 || dx < -512 || dx>512 || dy < -512 || dy>512)return 0;
        unsigned bytes=w*h/2;const uint8_t *raw;
        if(source>=0xff0000){if(!op_span(65536,source&65535,bytes))return 0;raw=ram+(source&65535);}
        else {if(!op_span(size,source,bytes))return 0;raw=rom+source;}
        total+=bytes;
        for(unsigned py=0;py<h;py++)for(unsigned px=0;px<w;px++) {
            unsigned at=((px/8)*(h/8)+py/8)*32+(py&7)*4+(px&7)/2;
            unsigned index=(raw[at]>>((px&1)?0:4))&15;int tx=x+dx+(int)px,ty=y+dy+(int)py;
            if(index && tx>=0 && tx<320 && ty>=0 && ty<224)canvas[ty*320+tx]=(uint8_t)(bank*16+index);
        }
    }
    return total==op_be16(rom+frame+10);
}
static int op_text(const uint8_t *rom,size_t size,uint8_t *ram,unsigned script,unsigned destination) {
    if(!op_span(size,script,6) || op_be32(rom+script)!=0xff0000u+destination)return 0;
    unsigned count=op_be16(rom+script+4);if(!count || count>64 || !op_span(size,script+6,count*2))return 0;
    unsigned characters=script+6+count*2;
    for(unsigned n=0;n<count;n++) {
        unsigned entry=op_be16(rom+script+6+n*2)>>6;if((entry&3) || entry>60)return 0;
        unsigned layout=op_be32(rom+0x291036+entry);if(!op_span(size,layout,1))return 0;
        unsigned tiles=rom[layout]+1,last=0;if(tiles>16 || !op_span(size,layout+1,tiles))return 0;
        for(unsigned i=0;i<tiles;i++) {
            last=rom[layout+1+i];if(!last || !op_span(size,characters,last))return 0;
            unsigned character=rom[characters+last-1];if(character<32 || character>127 || destination>65536-32)return 0;
            memcpy(ram+destination,ram+0x400+character*32,32);destination+=32;
        }
        characters+=last;
    }
    return 1;
}
int TlkOptionsArtPrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size) {
    static const uint8_t expected[32]={0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
    if(record)*record=NULL;if(record_size)*record_size=0;if(!record || !record_size || !rom || size!=0x300000)return 0;
    uint8_t hash[32];sha256_compute(rom,size,hash);if(memcmp(hash,expected,32))return 0;
    uint8_t *data=calloc(1,OPTIONS_RECORD),*tiles=calloc(1,65536),*maps=malloc(8192),*ram=calloc(1,65536),*selector_canvas=calloc(1,OPTIONS_PIXELS);
    int ok=0;size_t written=0;if(!data || !tiles || !maps || !ram || !selector_canvas)goto done;
    if(!TlkMdDecompress(rom,size,0x295864,tiles,65536,&written) || written!=29920 ||
       !TlkMdDecompress(rom,size,0x299414,maps,4096,&written) || written!=4096 ||
       !TlkMdDecompress(rom,size,0x2990ea,maps+4096,4096,&written) || written!=4096)goto done;
    for(unsigned i=0;i<4096;i++)if((op_be16(maps+i*2)&2047)>=935)goto done;
    uint8_t *p=data+112;
    for(unsigned i=0;i<64;i++){unsigned c=TlkMdColor555(op_be16(rom+0x2999ee + i*2));p[i*2]=(uint8_t)c;p[i*2+1]=(uint8_t)(c>>8);}
    uint8_t *base=p+128,*font=base+OPTIONS_PIXELS,*selector=font+96*64,*buttons=selector+576;
    op_plane(base,maps,tiles,0);op_plane(base,maps+4096,tiles,0);
    if(!TlkMdDecompress(rom,size,0x2910de,ram+0x800,3072,&written) || written!=3072)goto done;
    for(unsigned i=0;i<96;i++)for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++)font[i*64+y*8+x]=(ram[0x800+i*32+y*4+x/2]>>((x&1)?0:4))&15;
    if(!op_text(rom,size,ram,0x28e9b6,0x2200))goto done;
    const unsigned scripts[]={0x28ede0,0x28ee02,0x28ee34,0x28ee4e},destinations[]={0x3380,0x3640,0x3a60,0x3c60},frames[]={0x28eec2,0x28ef0a,0x28ef72,0x28efaa};
    for(unsigned i=0;i<4;i++)if(!op_text(rom,size,ram,scripts[i],destinations[i]))goto done;
    op_plane(base,maps,tiles,1);op_plane(base,maps+4096,tiles,1);
    if(!TlkMdDecompress(rom,size,0x29e4fa,ram+0x190,65536-0x190,&written) || written!=6272 ||
       !op_frame(base,rom,size,ram,0x29f5ea,0,32,7) || !op_frame(base,rom,size,ram,0x290c62,0,-16,6) ||
       !op_frame(selector_canvas,rom,size,ram,0x28fa92,11,8,0))goto done;
    /* Sprite overlap is resolved in SAT order before priority against planes.
     * The earlier Options labels win over the high-priority Rafiki/logo sprite;
     * drawing all low sprites before all high sprites hid parts of these words. */
    if(!op_frame(base,rom,size,ram,0x28ea52,32,176,2))goto done;
    for(unsigned i=0;i<4;i++)if(!op_frame(base,rom,size,ram,frames[i],64,80,2))goto done;
    for(unsigned y=0;y<24;y++)memcpy(selector+y*24,selector_canvas+y*320,24);
    const unsigned letters[]={0x28f11a,0x28f142,0x28f16a};
    for(unsigned i=0;i<18;i++) {
        unsigned frame=op_be32(rom+0x28ed98+i*4),j;for(j=0;j<3;j++)if(frame==letters[j])break;
        if(j==3)goto done;buttons[i]=(uint8_t)('a'+j);
    }
    memcpy(data,"TLKOPAR1",8);op_put32(data+8,1);op_put32(data+12,112);op_put32(data+16,OPTIONS_RECORD);op_put32(data+20,96);
    memcpy(data+24,expected,32);sha256_compute(data+112,OPTIONS_PAYLOAD,data+56);*record=data;*record_size=OPTIONS_RECORD;data=NULL;ok=1;
done:free(data);free(tiles);free(maps);free(ram);free(selector_canvas);return ok;
}

/* Original Sound Test295342 uses the existing two title planes and retained
 * logo/copyright sprites, replacing Options labels with seven circular rows.
 * Table29546C has sixteen18-byte entries and the8001/FFFF terminator. */
int TlkOptionsSoundTestPrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size) {
    enum { SOUND_TEST_RECORD=32+OPTIONS_PIXELS+16*18 };
    if(record)*record=NULL;if(record_size)*record_size=0;if(!record || !record_size)return 0;
    /* Reuse the existing strict original-ROM identity check. Its complete
     * result is discarded here; this function prepares a separate record. */
    uint8_t *verified=NULL;size_t verified_size=0;
    if(!TlkOptionsArtPrepare(rom,size,&verified,&verified_size))return 0;free(verified);
    uint8_t *data=calloc(1,SOUND_TEST_RECORD),*tiles=malloc(65536),*maps=malloc(8192),*ram=calloc(1,65536);int ok=0;size_t written=0;
    if(!data || !tiles || !maps || !ram)goto done;
    if(!TlkMdDecompress(rom,size,0x295864,tiles,65536,&written) || written!=29920 ||
       !TlkMdDecompress(rom,size,0x299414,maps,4096,&written) || written!=4096 ||
       !TlkMdDecompress(rom,size,0x2990ea,maps+4096,4096,&written) || written!=4096)goto done;
    for(unsigned i=0;i<4096;i++)if((op_be16(maps+i*2)&2047)>=935)goto done;
    uint8_t *base=data+32;op_plane(base,maps,tiles,0);op_plane(base,maps+4096,tiles,0);
    if(!TlkMdDecompress(rom,size,0x2910de,ram+0x800,3072,&written) || written!=3072 ||
       !op_text(rom,size,ram,0x28e9b6,0x2200) || !op_frame(base,rom,size,ram,0x28ea52,32,176,2))goto done;
    op_plane(base,maps,tiles,1);op_plane(base,maps+4096,tiles,1);
    if(!TlkMdDecompress(rom,size,0x29e4fa,ram+0x190,65536-0x190,&written) || written!=6272 ||
       !op_frame(base,rom,size,ram,0x29f5ea,0,32,7) || !op_frame(base,rom,size,ram,0x290c62,0,-16,6))goto done;
    if(!op_span(size,0x29546c,16*18+4) || op_be32(rom+0x29546c+16*18)!=0x8001ffffu)goto done;
    for(unsigned i=0;i<16;i++) {
        const uint8_t *source=rom+0x29546c+i*18;uint8_t *target=base+OPTIONS_PIXELS+i*18;unsigned program=op_be16(source);
        if(!program || program>432)goto done;target[0]=(uint8_t)program;target[1]=(uint8_t)(program>>8);
        for(unsigned j=0;j<16;j++){if(source[2+j]<32 || source[2+j]>127)goto done;target[2+j]=source[2+j];}
    }
    memcpy(data,"TLKSTST1",8);op_put32(data+8,1);op_put32(data+12,SOUND_TEST_RECORD);op_put32(data+16,16);op_put32(data+20,320);op_put32(data+24,224);
    *record=data;*record_size=SOUND_TEST_RECORD;data=NULL;ok=1;
done:free(data);free(tiles);free(maps);free(ram);return ok;
}

/* Original cheat/level-select menu295590: low-priority labels over the
 * shared title planes, high-priority selector,14 authored20-byte names. */
int TlkOptionsDebugMenuPrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size) {
    if(record)*record=NULL;if(record_size)*record_size=0;
    if(!record || !record_size)return 0;
    uint8_t *data=NULL,*ram=calloc(1,65536),*labels=calloc(1,OPTIONS_PIXELS);
    size_t data_size=0,written=0;int ok=0;
    if(!ram || !labels || !TlkOptionsSoundTestPrepare(rom,size,&data,&data_size) || data_size!=72000 ||
       !TlkMdDecompress(rom,size,0x2910de,ram+0x800,3072,&written) || written!=3072 ||
       !op_text(rom,size,ram,0x28f294,0x4aa0) ||
       !op_frame(labels,rom,size,ram,0x28f2bc,40,120,2))goto done;
    for(unsigned i=0;i<OPTIONS_PIXELS;i++)if(labels[i] && !(data[32+i]&64))data[32+i]=labels[i];
    memcpy(data,"TLKDBUG1",8);op_put32(data+12,32+OPTIONS_PIXELS+14*20);op_put32(data+16,14);
    memcpy(data+32+OPTIONS_PIXELS,rom+0x290d76,14*20);
    *record=data;*record_size=32+OPTIONS_PIXELS+14*20;data=NULL;ok=1;
done:free(data);free(ram);free(labels);return ok;
}
