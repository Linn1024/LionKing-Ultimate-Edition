#include "tlk_final_art_internal.h"
#include "tlk_final_art_prepare.h"
#include "tlk_options_art_prepare.h"
#include "tlk_final_native_internal.h"
#include "tlk_md_assets.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>

enum { BANK_SOURCE=0x299a6e,BANK_BASE=0x190,BANK_SIZE=27872,MAX_FRAMES=256,MAX_PIECES=80 };
typedef struct FinalPiece { int x,y;unsigned w,h;const uint8_t *pixels; } FinalPiece;
static unsigned be16(const uint8_t *p) { return (unsigned)p[0]<<8|p[1]; }
static uint32_t be32(const uint8_t *p) { return (uint32_t)be16(p)<<16|be16(p+2); }
static int signed16(unsigned v) { return v<32768?(int)v:(int)v-65536; }
static int span(size_t size,uint32_t at,size_t length) { return at<=size && length<=size-at; }
static int verified(const uint8_t *rom,size_t size) {
    static const uint8_t expected[32]={
        0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,
        0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
    uint8_t actual[32];if(!rom || size!=0x300000)return 0;
    sha256_compute(rom,size,actual);return !memcmp(actual,expected,32);
}
static int decode_frame(FinalImage *image,const uint8_t *rom,size_t size,const uint8_t *bank,uint32_t frame) {
    if(!span(size,frame,24))return 0;
    unsigned count=be16(rom+frame)+1,total=0;
    if(!count || count>MAX_PIECES || !span(size,frame+24,count*16) ||
       be16(rom+frame+6)>320 || be16(rom+frame+8)>224)return 0;
    FinalPiece pieces[MAX_PIECES];int left=512,top=512,right=-512,bottom=-512;
    for(unsigned i=0;i<count;i++) {
        const uint8_t *p=rom+frame+24+i*16;FinalPiece *piece=pieces+i;
        piece->w=be16(p);piece->h=be16(p+2);piece->x=signed16(be16(p+4));piece->y=signed16(be16(p+6));
        if(!piece->w || piece->w>32 || (piece->w&7) || !piece->h || piece->h>32 || (piece->h&7) ||
           piece->x < -512 || piece->x>512 || piece->y < -512 || piece->y>512)return 0;
        unsigned flags=be16(p+8),expected=((piece->w/8-1)<<2)|(piece->h/8-1);
        if(flags!=(expected<<8))return 0; /* Unreviewed piece flags request fallback. */
        size_t bytes=piece->w*piece->h/2;uint32_t source=be32(p+12);
        /* Original menu text includes sign-extended absolute-short RAM
         * pointers. The MD address bus uses the low24 bits in either form. */
        if((source>>24)!=0 && (source>>24)!=255)return 0;source&=0xffffff;
        if(source>=0xff0000) {
            if(source<0xff0000+BANK_BASE || !span(BANK_SIZE,source-0xff0000-BANK_BASE,bytes))return 0;
            piece->pixels=bank+(source-0xff0000-BANK_BASE);
        } else {
            if(!span(size,source,bytes))return 0;piece->pixels=rom+source;
        }
        total+=(unsigned)bytes;
        if(piece->x<left)left=piece->x;if(piece->y<top)top=piece->y;
        if(piece->x+(int)piece->w>right)right=piece->x+(int)piece->w;
        if(piece->y+(int)piece->h>bottom)bottom=piece->y+(int)piece->h;
    }
    if(total!=be16(rom+frame+10) || right<=left || bottom<=top || right-left>512 || bottom-top>512)return 0;
    image->x=left;image->y=top;image->w=right-left;image->h=bottom-top;image->frame=frame;
    image->pixels=calloc((size_t)image->w*image->h,1);if(!image->pixels)return 0;
    for(unsigned remaining=count;remaining;remaining--) {
        const FinalPiece *p=pieces+remaining-1;
        for(unsigned y=0;y<p->h;y++)for(unsigned x=0;x<p->w;x++) {
            size_t at=((x/8)*(p->h/8)+y/8)*32+(y&7)*4+(x&7)/2;
            unsigned index=(p->pixels[at]>>((x&1)?0:4))&15;
            if(index)image->pixels[(size_t)(p->y-top+(int)y)*image->w+p->x-left+x]=(uint8_t)index;
        }
    }
    return 1;
}
static TlkFinalArt *prepare_images(const uint8_t *rom,size_t size,const uint32_t *frames,unsigned count) {
    if(!frames || !count || count>MAX_FRAMES || !verified(rom,size))return NULL;
    uint8_t *bank=malloc(0x8000);TlkFinalArt *art=calloc(1,sizeof *art);size_t written=0;
    if(!bank || !art) {free(bank);free(art);return NULL;}
    if(!TlkMdDecompress(rom,size,BANK_SOURCE,bank,0x8000,&written) || written!=BANK_SIZE)goto fail;
    art->images=calloc(count,sizeof *art->images);if(!art->images)goto fail;art->count=count;
    for(unsigned i=0;i<count;i++) {
        for(unsigned j=0;j<i;j++)if(frames[i]==frames[j])goto fail;
        if(!decode_frame(art->images+i,rom,size,bank,frames[i]))goto fail;
    }
    for(unsigned i=0;i<64;i++)art->palette[i]=TlkMdColor555(be16(rom+0x1d78aa+i*2));
    free(bank);return art;
fail:
    free(bank);TlkFinalArtFree(art);return NULL;
}
static void put32(uint8_t *p,uint32_t value) {
    for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(value>>(i*8));
}
int TlkFinalArtPrepare(const uint8_t *rom,size_t size,const uint32_t *frames,unsigned count,
                      uint8_t **record,size_t *record_size) {
    if(record)*record=NULL;if(record_size)*record_size=0;
    if(!record || !record_size)return 0;
    TlkFinalArt *art=prepare_images(rom,size,frames,count);if(!art)return 0;
    size_t bytes=112+128;
    for(unsigned i=0;i<count;i++)bytes+=20+(size_t)art->images[i].w*art->images[i].h;
    uint8_t *data=calloc(1,bytes);if(!data){TlkFinalArtFree(art);return 0;}
    memcpy(data,"TLKFMAR1",8);put32(data+8,1);put32(data+12,112);
    put32(data+16,(uint32_t)bytes);put32(data+20,count);sha256_compute(rom,size,data+24);
    uint8_t *p=data+112;
    for(unsigned i=0;i<64;i++) { *p++=(uint8_t)art->palette[i];*p++=(uint8_t)(art->palette[i]>>8); }
    for(unsigned i=0;i<count;i++) {
        const FinalImage *image=art->images+i;
        put32(p,image->frame);put32(p+4,(uint32_t)image->x);put32(p+8,(uint32_t)image->y);
        put32(p+12,(uint32_t)image->w);put32(p+16,(uint32_t)image->h);p+=20;
        size_t n=(size_t)image->w*image->h;memcpy(p,image->pixels,n);p+=n;
    }
    sha256_compute(data+112,bytes-112,data+56);TlkFinalArtFree(art);
    *record=data;*record_size=bytes;return 1;
}
static int inventory_add(uint32_t *frames,unsigned *count,uint32_t frame) {
    for(unsigned i=0;i<*count;i++)if(frames[i]==frame)return 1;
    if(*count==MAX_FRAMES)return 0;frames[(*count)++]=frame;return 1;
}
static int inventory_animation(const uint8_t *rom,size_t size,uint32_t start,uint32_t *frames,unsigned *count) {
    uint32_t visited[256],pc=start;unsigned steps=0;
    while(steps<256) {
        for(unsigned i=0;i<steps;i++)if(visited[i]==pc)return 1;
        if((pc&1) || !span(size,pc,4))return 0;visited[steps++]=pc;
        uint32_t command=be32(rom+pc),value=command&0xffffffu;unsigned duration=command>>24;
        if(duration==255) {pc=value;continue;}
        if(!duration || !inventory_add(frames,count,value))return 0;
        pc+=4;
    }
    return 0;
}
static int prepare_program(const uint8_t *rom,size_t size,uint32_t pc,FinalStep *steps,unsigned *count,unsigned *loop) {
    uint32_t addresses[256];*count=0;
    for(unsigned operations=0;operations<512;operations++) {
        for(unsigned i=0;i<*count;i++)if(addresses[i]==pc){*loop=i;return 1;}
        if((pc&1) || !span(size,pc,4))return 0;
        uint32_t command=be32(rom+pc),value=command&0xffffffu;unsigned duration=command>>24;
        if(duration==255){pc=value;continue;}
        if(!duration || *count==256)return 0;
        addresses[*count]=pc;steps[*count].frame=value;steps[*count].ticks=duration+1;(*count)++;pc+=4;
    }
    return 0;
}
#include "tlk_ready_title_prepare.inc"
#include "tlk_title_opening_prepare.inc"
#include "tlk_publisher_prepare.inc"
int TlkFinalArtPrepareMenus(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size) {
    if(record)*record=NULL;if(record_size)*record_size=0;
    if(!record || !record_size || !verified(rom,size))return 0;
    uint32_t frames[MAX_FRAMES];unsigned count=0;
    /* Original descriptor graphics pointers: Continue text, Game Over text,
     * selection hand. These descriptors are selected by the original setup. */
    const uint32_t descriptors[]={0x1d679c,0x1d67a6,0x1d6756};
    for(unsigned i=0;i<3;i++)if(!inventory_add(frames,&count,be32(rom+descriptors[i]+6)))return 0;
    if(!inventory_animation(rom,size,0x1d67d8,frames,&count) ||
       !inventory_animation(rom,size,0x1d6828,frames,&count))return 0;
    for(unsigned i=0;i<10;i++)if(!inventory_add(frames,&count,be32(rom+0x1cee60+i*4)))return 0;
    /* Menu sets credit-icon state1; its original action selects this stream
     * through the four-entry state table, then the stream descriptor. */
    uint32_t icon=be32(rom+0x8ea80+4);
    if(!span(size,icon,6) || be16(rom+icon) ||
       !inventory_animation(rom,size,be32(rom+icon+2),frames,&count))return 0;
    FinalStep steps[3][256];unsigned lengths[3],loops[3];
    const uint32_t programs[]={0x1d67d8,0x1d6828,be32(rom+icon+2)};
    size_t plan_size=104+3*8;
    for(unsigned i=0;i<3;i++) {
        if(!prepare_program(rom,size,programs[i],steps[i],lengths+i,loops+i))return 0;
        plan_size+=lengths[i]*8;
    }
    if(!TlkFinalArtPrepare(rom,size,frames,count,record,record_size))return 0;
    uint8_t *title=NULL;size_t title_size=0;
    if(!prepare_ready_title(rom,size,&title,&title_size)){free(*record);*record=NULL;*record_size=0;return 0;}
    uint8_t *options=NULL;size_t options_size=0;
    if(!TlkOptionsArtPrepare(rom,size,&options,&options_size)){free(title);free(*record);*record=NULL;*record_size=0;return 0;}
    uint8_t *opening=NULL;size_t opening_size=0;
    if(!prepare_title_opening(rom,size,&opening,&opening_size)){free(options);free(title);free(*record);*record=NULL;*record_size=0;return 0;}
    uint8_t *publisher=NULL;size_t publisher_size=0;
    if(!prepare_publisher(rom,size,&publisher,&publisher_size)){free(opening);free(options);free(title);free(*record);*record=NULL;*record_size=0;return 0;}
    uint8_t *sound=NULL;size_t sound_size=0;
    if(!TlkOptionsSoundTestPrepare(rom,size,&sound,&sound_size)){free(publisher);free(opening);free(options);free(title);free(*record);*record=NULL;*record_size=0;return 0;}
    uint8_t *debug=NULL;size_t debug_size=0;
    if(!TlkOptionsDebugMenuPrepare(rom,size,&debug,&debug_size)){free(sound);free(publisher);free(opening);free(options);free(title);free(*record);*record=NULL;*record_size=0;return 0;}
    size_t size_v1=*record_size,total=size_v1+plan_size+title_size+options_size+opening_size+publisher_size+sound_size+debug_size;
    uint8_t *data=calloc(1,total);
    if(!data){free(debug);free(sound);free(publisher);free(opening);free(options);free(title);free(*record);*record=NULL;*record_size=0;return 0;}
    memcpy(data,*record,size_v1);free(*record);uint8_t *p=data+size_v1;
    for(unsigned i=0;i<3;i++,p+=4)put32(p,be32(rom+descriptors[i]+6));
    for(unsigned i=0;i<10;i++,p+=4)put32(p,be32(rom+0x1cee60+i*4));
    /* Original setup instruction immediates: Rafiki Y, selector left/right/Y,
     * icon X/Y and digit X/Y. Playback never reads these ROM locations. */
    const uint32_t coordinates[]={0x1d6a1e,0x1d6a3a,0x1d6786,0x1d6a34,
        0x1d6a00,0x1d6a06,0x1d69e2,0x1d69e8};
    for(unsigned i=0;i<8;i++,p+=4)put32(p,(uint32_t)signed16(be16(rom+coordinates[i])));
    const uint32_t palette_descriptors[]={0x1d679c,0x1d67b2,0x1d6756,0x8ea90,0x1ce08c};
    for(unsigned i=0;i<5;i++,p+=4)put32(p,(be16(rom+palette_descriptors[i]+4)>>13)&3);
    for(unsigned i=0;i<3;i++) {
        put32(p,lengths[i]);put32(p+4,loops[i]);p+=8;
        for(unsigned j=0;j<lengths[i];j++,p+=8){put32(p,steps[i][j].frame);put32(p+4,steps[i][j].ticks);}
    }
    memcpy(p,title,title_size);free(title);p+=title_size;memcpy(p,options,options_size);free(options);p+=options_size;memcpy(p,opening,opening_size);free(opening);p+=opening_size;memcpy(p,publisher,publisher_size);free(publisher);p+=publisher_size;memcpy(p,sound,sound_size);free(sound);p+=sound_size;memcpy(p,debug,debug_size);free(debug);
    put32(data+8,8);put32(data+16,(uint32_t)total);put32(data+88,(uint32_t)plan_size);put32(data+92,(uint32_t)title_size);put32(data+96,(uint32_t)options_size);put32(data+100,(uint32_t)opening_size);put32(data+104,(uint32_t)publisher_size);put32(data+108,(uint32_t)(sound_size+debug_size));
    sha256_compute(data+112,total-112,data+56);*record=data;*record_size=total;return 1;
}

/* Menu-v9 adds only the original SNES catalogue text. Graphics and playback
 * source selection remain independent; all old menu payload bytes retained. */
int TlkFinalArtPrepareMenuSources(const uint8_t *md,size_t md_size,const uint8_t *snes,size_t snes_size,
                                 uint8_t **record,size_t *record_size) {
    if(record)*record=NULL;if(record_size)*record_size=0;
    if(!record || !record_size || !snes || snes_size!=0x300000)return 0;
    uint8_t hash[32];sha256_compute(snes,snes_size,hash);if(memcmp(hash,tlk_final_native_source,32))return 0;
    uint8_t *old=NULL;if(!TlkFinalArtPrepareMenus(md,md_size,&old,record_size))return 0;
    size_t old_size=*record_size,total=old_size+NATIVE_SOUND_CATALOG_BYTES+ATTRACT_BYTES;*record_size=0;
    uint8_t *data=realloc(old,total);if(!data){free(old);return 0;}
    uint8_t *catalog=data+old_size;memset(catalog,0,NATIVE_SOUND_CATALOG_BYTES);memset(catalog+64,' ',16*20);
    memcpy(catalog,"TLKSCAT1",8);put32(catalog+8,1);put32(catalog+12,NATIVE_SOUND_CATALOG_BYTES);
    put32(catalog+16,16);put32(catalog+20,20);memcpy(catalog+24,tlk_final_native_source,32);
    for(unsigned i=0;i<16;i++) {
        unsigned at=0x3b90c+(0x3d+i)*4;uint32_t address=snes[at]|(uint32_t)snes[at+1]<<8|(uint32_t)snes[at+2]<<16;
        if((address>>16)!=0xc3){free(data);return 0;}
        at=address&0x3fffff;unsigned n=0;
        for(;n<20 && snes[at+n];n++){unsigned c=snes[at+n];if(c<32 || c>127){free(data);return 0;}catalog[64+i*20+n]=(uint8_t)c;}
        if(!n || snes[at+n]){free(data);return 0;}
    }
    /* Original MD demo initialization1D7786 and controller playbackC58.
     * Keep the packed controller runs as installed data, never execute ROM code. */
    uint8_t *demo=catalog+NATIVE_SOUND_CATALOG_BYTES;memset(demo,0,ATTRACT_BYTES);
    memcpy(demo,"TLKDEMO1",8);put32(demo+8,1);put32(demo+12,ATTRACT_BYTES);put32(demo+16,3);
    const unsigned levels[3]={0,2,8},starts[3]={0x28e4dc,0x28e59c,0x28e60c};
    for(unsigned i=0;i<3;i++) {
        uint8_t *row=demo+64+i*168;put32(row,levels[i]);unsigned n=0;
        for(;n<80;n++) {
            unsigned at=starts[i]+n*2;if(at+2>md_size){free(data);return 0;}
            row[8+n*2]=md[at];row[9+n*2]=md[at+1];
            if(md[at]==255 && md[at+1]==255){n++;break;}
        }
        if(!n || n>80 || row[8+(n-1)*2]!=255 || row[9+(n-1)*2]!=255){free(data);return 0;}
        put32(row+4,n);
    }
    put32(data+8,10);put32(data+16,(uint32_t)total);
    put32(data+108,(uint32_t)(SOUND_TEST_BYTES+DEBUG_MENU_BYTES+NATIVE_SOUND_CATALOG_BYTES+ATTRACT_BYTES));
    sha256_compute(data+112,total-112,data+56);*record=data;*record_size=total;return 1;
}
