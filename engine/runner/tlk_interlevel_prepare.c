/* Installer only: translate the reviewed Pride completion artwork/programs. */
#include "tlk_interlevel_data.h"
#include "tlk_data_record.h"
#include "tlk_md_assets.h"
#include <stdlib.h>
#include <string.h>

enum { MAX_IMAGES=64,MAX_STEPS=128,SCREEN=320*224 };
typedef struct {unsigned source,w,h;int x,y;uint8_t *pixels;} Image;
typedef struct {unsigned frame,ticks,events,address;} Step;
typedef struct {Step steps[MAX_STEPS];unsigned count,loop;} Program;
typedef struct {unsigned w,h,source;int x,y;} Piece;
static unsigned be16(const uint8_t *p){return (unsigned)p[0]<<8|p[1];}
static unsigned be32(const uint8_t *p){return be16(p)<<16|be16(p+2);}
static int signed16(unsigned v){return v<32768?(int)v:(int)v-65536;}
static int image_decode(const uint8_t *rom,const uint8_t *bank,size_t bank_size,unsigned source,Image *out){
    if(source>0x300000-24)return 0;unsigned count=be16(rom+source)+1;
    if(!count || count>32 || source+24+count*16>0x300000)return 0;
    Piece pieces[32];int left=512,top=512,right=-512,bottom=-512;unsigned bytes=0;
    for(unsigned i=0;i<count;i++){
        const uint8_t *p=rom+source+24+i*16;Piece *q=pieces+i;
        q->w=be16(p);q->h=be16(p+2);q->x=signed16(be16(p+4));q->y=signed16(be16(p+6));q->source=be32(p+12);
        if(!q->w || q->w>32 || (q->w&7) || !q->h || q->h>32 || (q->h&7) ||
           be16(p+8)!=(((q->w/8-1)*4+q->h/8-1)<<8) || q->x<-256 || q->x>256 || q->y<-224 || q->y>224)return 0;
        unsigned size=q->w*q->h/2;
        if(q->source>=0xff0000){if(q->source<0xff0190 || q->source-0xff0190>bank_size || size>bank_size-(q->source-0xff0190))return 0;}
        else if(q->source>0x300000 || size>0x300000-q->source)return 0;
        if(q->x<left)left=q->x;if(q->y<top)top=q->y;
        if(q->x+(int)q->w>right)right=q->x+q->w;if(q->y+(int)q->h>bottom)bottom=q->y+q->h;bytes+=size;
    }
    if(bytes!=be16(rom+source+10) || right<=left || bottom<=top || right-left>256 || bottom-top>224)return 0;
    out->source=source;out->x=left;out->y=top;out->w=right-left;out->h=bottom-top;
    out->pixels=calloc(out->w*out->h,1);if(!out->pixels)return 0;
    for(unsigned remaining=count;remaining;remaining--){
        const Piece *p=pieces+remaining-1;const uint8_t *data=p->source>=0xff0000?bank+p->source-0xff0190:rom+p->source;
        for(unsigned y=0;y<p->h;y++)for(unsigned x=0;x<p->w;x++){
            unsigned at=((x/8)*(p->h/8)+y/8)*32+(y&7)*4+(x&7)/2;
            unsigned value=(data[at]>>((x&1)?0:4))&15;
            if(value)out->pixels[(p->y-top+y)*out->w+p->x-left+x]=value;
        }
    }
    return 1;
}
static int inventory(const uint8_t *rom,const uint8_t *bank,size_t bank_size,unsigned frame,Image *images,unsigned *count){
    for(unsigned i=0;i<*count;i++)if(images[i].source==frame)return (int)i;
    if(*count>=MAX_IMAGES || !image_decode(rom,bank,bank_size,frame,images+*count))return -1;
    return (int)(*count)++;
}
static int translate_until(const uint8_t *rom,const uint8_t *bank,size_t bank_size,unsigned pc,Program *program,Image *images,unsigned *count,unsigned end_event){
    unsigned events=0;
    for(unsigned operations=0;operations<512;operations++){
        for(unsigned i=0;i<program->count;i++)if(program->steps[i].address==pc){if(events)return 0;program->loop=i;return 1;}
        if(pc>0x300000-4 || program->count==MAX_STEPS)return 0;
        unsigned command=rom[pc];
        if(command==255){pc=be32(rom+pc)&0xffffff;continue;}
        if(command==253){
            unsigned event=rom[pc+1];if(event<1 || event>3)return 0;events|=1u<<event;pc+=2;
            if(event==end_event){
                if(!program->count)return 0;program->loop=program->count;
                program->steps[program->count]=(Step){program->steps[program->count-1].frame,1,events,pc};program->count++;return 1;
            }
            continue;
        }
        if(command>=253)return 0;
        int frame=inventory(rom,bank,bank_size,be32(rom+pc)&0xffffff,images,count);if(frame<0)return 0;
        program->steps[program->count++]=(Step){(unsigned)frame,command+1,events,pc};events=0;pc+=4;
    }
    return 0;
}
static int translate(const uint8_t *rom,const uint8_t *bank,size_t bank_size,unsigned pc,Program *program,Image *images,unsigned *count){
    return translate_until(rom,bank,bank_size,pc,program,images,count,1);
}
static void plane(uint8_t *pixels,const uint8_t *map,const uint8_t *tiles,unsigned priority){
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<320;x++){
        unsigned n=be16(map+((y/8)*64+x/8)*2);if(!!(n&0x8000)!=priority)continue;
        unsigned xx=n&0x800?7-x%8:x%8,yy=n&0x1000?7-y%8:y%8;
        unsigned value=(tiles[(n&2047)*32+yy*4+xx/2]>>((xx&1)?0:4))&15;
        if(value)pixels[y*320+x]=((n>>13)&3)*16+value;
    }
}
enum { CREDIT_FONT=192,CREDIT_TILES=37,CREDIT_MAP=192+37*64,CREDIT_SIZE=CREDIT_MAP+260*80 };
static int prepare_credits(const uint8_t *m,size_t mn,uint8_t *out){
    uint8_t font[1184],map[20800];size_t n=0;
    if(be32(m+0x1ceea2)!=0x1cfb98 || be32(m+0x1ceed6)!=0x1cef78 ||
       be32(m+0x1cee96)!=0x1cfd34 ||
       !TlkMdDecompress(m,mn,0x1cfb98,font,sizeof font,&n) || n!=sizeof font ||
       !TlkMdDecompress(m,mn,0x1cef78,map,sizeof map,&n) || n!=sizeof map)return 0;
    memset(out,0,CREDIT_SIZE);memcpy(out,"TLKCRD01",8);TlkDataPut32(out+8,1);
    TlkDataPut32(out+12,CREDIT_SIZE);TlkDataPut32(out+16,260);TlkDataPut32(out+20,CREDIT_TILES);
    TlkDataPut32(out+24,CREDIT_FONT);TlkDataPut32(out+28,CREDIT_MAP);
    for(unsigned i=0;i<64;i++)TlkDataPut16(out+64+i*2,TlkMdColor555(be16(m+0x1cfd34+i*2)));
    for(unsigned i=0;i<CREDIT_TILES;i++)for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++)
        out[CREDIT_FONT+i*64+y*8+x]=(font[i*32+y*4+x/2]>>((x&1)?0:4))&15;
    for(unsigned i=0;i<sizeof map;i+=2){unsigned v=be16(map+i);
        if((v&0x7ff)>=CREDIT_TILES || (v&0xf800 && (v&0xf800)!=0x2000))return 0;
        TlkDataPut16(out+CREDIT_MAP+i,(uint16_t)v);}
    return 1;
}
#include "tlk_cliff_prepare.inc"
#include "tlk_timon_prepare.inc"
int TlkInterlevelDataPrepare(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    if(!s || !m || sn!=0x300000 || mn!=0x300000)return 0;
    /* Original reviewed initialization operands: two planes and animation bank. */
    if(be16(m+0x29585c)!=0x83e8 || be32(m+0x29585e)!=0x295864 || be16(m+0x295862) ||
       be32(m + 0x18d968 + 2)!=0x29585c || be32(m + 0x18d9ae + 2)!=0x18dbf0)return 0;
    uint8_t *tiles=malloc(65536),*maps=malloc(8192),*bank=malloc(32768),*bg=calloc(SCREEN,1),*data=NULL;
    Image images[MAX_IMAGES]={0};Program programs[2]={0};unsigned count=0;size_t n=0,bank_size=0,total=0;int ok=0;
    if(!tiles || !maps || !bank || !bg)goto done;
    if(!TlkMdDecompress(m,mn,0x295864,tiles,65536,&n) || n!=29920 ||
       !TlkMdDecompress(m,mn,0x2990ea,maps,4096,&n) || n!=4096 ||
       !TlkMdDecompress(m,mn,0x299414,maps+4096,4096,&n) || n!=4096 ||
       !TlkMdDecompress(m,mn,0x18dbf0,bank,32768,&bank_size) || bank_size!=4256)goto done;
    for(unsigned i=0;i<8192;i+=2)if((be16(maps+i)&2047)>=935)goto done;
    plane(bg,maps+4096,tiles,0);plane(bg,maps,tiles,0);plane(bg,maps+4096,tiles,1);plane(bg,maps,tiles,1);
    if(!translate(m,bank,bank_size,0x18dae8,programs,images,&count) ||
       !translate(m,bank,bank_size,0x18db0a,programs+1,images,&count))goto done;
    /* Ending1CDEA0 creates a static title actor, not a Simba roar animation.
     * Its original descriptor flagsE040 select palette3, origin0/0. */
    if(be32(m+0x1cdeee)!=0x67b0e040 || be32(m+0x1cdef2)!=0x00290c62 ||
       inventory(m,bank,bank_size,0x290c62,images,&count)<0)goto done;
    unsigned program_at=192+SCREEN,image_at=program_at+(programs[0].count+programs[1].count)*12;
    total=image_at+0x4756+0x2922+CREDIT_SIZE;for(unsigned i=0;i<count;i++)total+=16+images[i].w*images[i].h;
    data=calloc(1,total);if(!data)goto done;
    memcpy(data,"TLKILV01",8);TlkDataPut32(data+8,2);TlkDataPut32(data+12,(uint32_t)total);TlkDataPut32(data+16,count);
    for(unsigned i=0;i<2;i++){TlkDataPut32(data+20+i*4,programs[i].count);TlkDataPut32(data+28+i*4,programs[i].loop);}
    TlkDataPut32(data+36,image_at);TlkDataPut32(data+40,program_at);TlkDataPut32(data+44,192);
    TlkDataPut32(data+52,0x4756);TlkDataPut32(data+56,0x2922);
    for(unsigned i=0;i<64;i++)TlkDataPut16(data+64+i*2,TlkMdColor555(be16(m+0x18db70+i*2)));
    memcpy(data+192,bg,SCREEN);size_t at=program_at;
    for(unsigned i=0;i<2;i++)for(unsigned k=0;k<programs[i].count;k++){
        const Step *step=programs[i].steps+k;TlkDataPut32(data+at,step->frame);TlkDataPut32(data+at+4,step->ticks);TlkDataPut32(data+at+8,step->events);at+=12;
    }
    for(unsigned i=0;i<count;i++){
        const Image *f=images+i;TlkDataPut32(data+at,f->source);TlkDataPut16(data+at+4,(uint16_t)f->x);TlkDataPut16(data+at+6,(uint16_t)f->y);
        TlkDataPut16(data+at+8,f->w);TlkDataPut16(data+at+10,f->h);TlkDataPut32(data+at+12,f->w*f->h);memcpy(data+at+16,f->pixels,f->w*f->h);at+=16+f->w*f->h;
    }
    TlkDataPut32(data+48,(uint32_t)at);memcpy(data+at,m+0x2d8000,0x4756+0x2922);at+=0x4756+0x2922;
    TlkDataPut32(data+60,(uint32_t)at);if(!prepare_credits(m,mn,data+at))goto done;at+=CREDIT_SIZE;
    if(at!=total)goto done;
    uint8_t *cliff=NULL;size_t cliff_size=0;
    if(!prepare_cliff(m,mn,&cliff,&cliff_size))goto done;
    uint8_t *extended=realloc(data,total+cliff_size);
    if(!extended){free(cliff);goto done;}data=extended;
    memcpy(data+total,cliff,cliff_size);free(cliff);total+=cliff_size;
    uint8_t *timon=NULL;size_t timon_size=0;
    if(!prepare_timon(s,m,&timon,&timon_size))goto done;
    extended=realloc(data,total+timon_size);if(!extended){free(timon);goto done;}data=extended;
    memcpy(data+total,timon,timon_size);free(timon);total+=timon_size;
    TlkDataPut32(data+8,4);TlkDataPut32(data+12,(uint32_t)total);
    ok=TlkInterlevelDataRead(data,total,1);
done:
    for(unsigned i=0;i<MAX_IMAGES;i++)free(images[i].pixels);free(data);free(tiles);free(maps);free(bank);free(bg);return ok;
}
