#include "tlk_final_art_internal.h"
#include "tlk_final_native_internal.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>

int TlkFinalArtAttractRun(const TlkFinalArt *art,unsigned level,unsigned run,unsigned *pad,unsigned *duration) {
    if(!art || !art->attract || !pad || !duration)return 0;
    unsigned slot=level==0?0:level==2?1:level==8?2:3;if(slot==3)return 0;
    const uint8_t *row=art->attract+64+slot*168;
    unsigned n=(unsigned)row[4]|(unsigned)row[5]<<8;
    if(run>=n)return 0;
    unsigned bits=row[8+run*2],ticks=row[9+run*2];
    if(bits==255 && ticks==255){*pad=65535;*duration=0;return 1;}
    *pad=((bits&1)?0x800:0)|((bits&2)?0x400:0)|((bits&4)?0x200:0)|((bits&8)?0x100:0)|
         ((bits&16)?0x4000:0)|((bits&32)?0x8000:0)|((bits&64)?0x80:0)|((bits&128)?0x1000:0);
    *duration=ticks+(run?1:0);return *duration!=0;
}
static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
#include "tlk_publisher_art.inc"
static int signed_position(uint32_t value,int *out) {
    int64_t n=value<=0x7fffffffu?(int64_t)value:(int64_t)value-0x100000000ll;
    if(n < -512 || n>512)return 0;*out=(int)n;return 1;
}
static const FinalImage *find(const TlkFinalArt *,uint32_t);
TlkFinalArt *TlkFinalArtLoad(const uint8_t *data,size_t size) {
    static const uint8_t source[32]={
        0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,
        0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
    if(!data || size<240 || size>64u*1024*1024 || memcmp(data,"TLKFMAR1",8) ||
       (get32(data+8)<1 || get32(data+8)>10) || get32(data+12)!=112 || get32(data+16)!=size ||
       !get32(data+20) || get32(data+20)>256 || memcmp(data+24,source,32))return NULL;
    unsigned version=get32(data+8);size_t plan_size=version>=2?get32(data+88):0;
    size_t title_size=version>=3?get32(data+92):0;
    size_t options_size=version>=4?get32(data+96):0;
    size_t opening_size=version>=5?get32(data+100):0;
    size_t publisher_size=version>=6?get32(data+104):0;
    size_t sound_size=version>=7?get32(data+108):0;
    if((version>=2 && plan_size<152) || plan_size>size-240 ||
       (version>=3 && title_size!=128+320*224+24*24) || title_size>size-240-plan_size ||
       (version>=4 && options_size<112) || options_size>size-240-plan_size-title_size ||
       (version>=5 && opening_size<168+320*224) || opening_size>size-240-plan_size-title_size-options_size ||
       (version>=6 && publisher_size!=PUBLISHER_BYTES) || publisher_size>size-240-plan_size-title_size-options_size-opening_size ||
       (version>=7 && sound_size!=SOUND_TEST_BYTES+(version>=8?DEBUG_MENU_BYTES:0)+(version>=9?NATIVE_SOUND_CATALOG_BYTES:0)+(version>=10?ATTRACT_BYTES:0)) || sound_size>size-240-plan_size-title_size-options_size-opening_size-publisher_size)return NULL;
    for(unsigned i=version>=7?112:version==6?108:version==5?104:version==4?100:version==3?96:version==2?92:88;i<112;i++)if(data[i])return NULL;
    uint8_t hash[32];sha256_compute(data+112,size-112,hash);
    if(memcmp(hash,data+56,32))return NULL;
    TlkFinalArt *art=calloc(1,sizeof *art);if(!art)return NULL;
    art->count=get32(data+20);art->images=calloc(art->count,sizeof *art->images);
    if(!art->images){free(art);return NULL;}
    const uint8_t *p=data+112,*end=data+size-plan_size-title_size-options_size-opening_size-publisher_size-sound_size;
    for(unsigned i=0;i<64;i++,p+=2) {
        art->palette[i]=(uint16_t)(p[0]|(unsigned)p[1]<<8);
        if(art->palette[i]>0x7fff)goto fail;
    }
    for(unsigned i=0;i<art->count;i++) {
        if((size_t)(end-p)<20)goto fail;
        FinalImage *image=art->images+i;image->frame=get32(p);
        if(image->frame>=0x300000 || (image->frame&1) ||
           !signed_position(get32(p+4),&image->x) || !signed_position(get32(p+8),&image->y))goto fail;
        unsigned w=get32(p+12),h=get32(p+16);p+=20;
        if(!w || w>512 || !h || h>512 || (size_t)w*h>(size_t)(end-p))goto fail;
        for(unsigned j=0;j<i;j++)if(art->images[j].frame==image->frame)goto fail;
        size_t n=(size_t)w*h;
        for(size_t k=0;k<n;k++)if(p[k]>15)goto fail;
        image->w=(int)w;image->h=(int)h;image->pixels=malloc(n);
        if(!image->pixels)goto fail;memcpy(image->pixels,p,n);p+=n;
    }
    if(p!=end)goto fail;
    if(plan_size) {
        end=data+size-title_size-options_size-opening_size-publisher_size-sound_size;art->plan=calloc(1,sizeof *art->plan);if(!art->plan)goto fail;
        FinalPlan *plan=art->plan;
        for(unsigned i=0;i<13;i++,p+=4) {plan->slots[i]=get32(p);if(!find(art,plan->slots[i]))goto fail;}
        for(unsigned i=0;i<8;i++,p+=4)if(!signed_position(get32(p),plan->coordinates+i))goto fail;
        for(unsigned i=0;i<5;i++,p+=4) {plan->banks[i]=get32(p);if(plan->banks[i]>3)goto fail;}
        for(unsigned i=0;i<3;i++) {
            if((size_t)(end-p)<8)goto fail;
            FinalProgram *program=plan->programs+i;program->count=get32(p);program->loop=get32(p+4);p+=8;
            if(!program->count || program->count>256 || program->loop>=program->count ||
               (size_t)program->count*8>(size_t)(end-p))goto fail;
            program->steps=calloc(program->count,sizeof *program->steps);if(!program->steps)goto fail;
            for(unsigned j=0;j<program->count;j++,p+=8) {
                program->steps[j].frame=get32(p);program->steps[j].ticks=get32(p+4);
                if(!find(art,program->steps[j].frame) || !program->steps[j].ticks || program->steps[j].ticks>256)goto fail;
            }
        }
        if(p!=end)goto fail;
    }
    if(title_size) {
        art->title=calloc(1,sizeof *art->title);if(!art->title)goto fail;
        for(unsigned i=0;i<64;i++,p+=2) {
            unsigned c=p[0]|(unsigned)p[1]<<8;if(c>0x7fff)goto fail;
            art->title->palette[i]=(uint16_t)c;
        }
        for(unsigned i=0;i<320*224;i++,p++){if(*p>127)goto fail;art->title->base[i]=*p;}
        for(unsigned i=0;i<24*24;i++,p++){if(*p>15)goto fail;art->title->selector[i]=*p;}
        if(p!=data+size-options_size-opening_size-publisher_size-sound_size)goto fail;
    }
    if(options_size){art->options=TlkOptionsArtLoad(p,options_size);if(!art->options)goto fail;p+=options_size;}
    if(opening_size){art->opening=TlkTitleOpeningArtLoad(p,opening_size);if(!art->opening)goto fail;p+=opening_size;}
    if(publisher_size){art->publisher=publisher_load(p,publisher_size);if(!art->publisher)goto fail;p+=publisher_size;}
    if(sound_size) {
        if(!art->options || memcmp(p,"TLKSTST1",8) || get32(p+8)!=1 || get32(p+12)!=SOUND_TEST_BYTES ||
           get32(p+16)!=16 || get32(p+20)!=320 || get32(p+24)!=224 || get32(p+28))goto fail;
        for(unsigned i=0;i<320*224;i++)if(p[32+i]>127)goto fail;
        for(unsigned i=0;i<16;i++) {
            const uint8_t *entry=p+32+320*224+i*18;
            if(!(entry[0]|(unsigned)entry[1]<<8) || (entry[0]|(unsigned)entry[1]<<8)>0x7fff)goto fail;
            for(unsigned j=2;j<18;j++)if(entry[j]<32 || entry[j]>127)goto fail;
        }
        if(version>=8) {
            const uint8_t *debug=p+SOUND_TEST_BYTES;
            if(memcmp(debug,"TLKDBUG1",8) || get32(debug+8)!=1 || get32(debug+12)!=DEBUG_MENU_BYTES ||
               get32(debug+16)!=14 || get32(debug+20)!=320 || get32(debug+24)!=224 || get32(debug+28))goto fail;
            for(unsigned i=0;i<320*224;i++)if(debug[32+i]>127)goto fail;
            for(unsigned i=0;i<14*20;i++)if(debug[32+320*224+i]<32 || debug[32+320*224+i]>127)goto fail;
        }
        if(version>=9) {
            const uint8_t *catalog=p+SOUND_TEST_BYTES+DEBUG_MENU_BYTES;
            if(memcmp(catalog,"TLKSCAT1",8) || get32(catalog+8)!=1 || get32(catalog+12)!=NATIVE_SOUND_CATALOG_BYTES ||
               get32(catalog+16)!=16 || get32(catalog+20)!=20 || memcmp(catalog+24,tlk_final_native_source,32))goto fail;
            for(unsigned i=56;i<64;i++)if(catalog[i])goto fail;
            for(unsigned i=0;i<16*20;i++)if(catalog[64+i]<32 || catalog[64+i]>127)goto fail;
        }
        if(version>=10) {
            const uint8_t *demo=p+SOUND_TEST_BYTES+DEBUG_MENU_BYTES+NATIVE_SOUND_CATALOG_BYTES;
            if(memcmp(demo,"TLKDEMO1",8) || get32(demo+8)!=1 || get32(demo+12)!=ATTRACT_BYTES || get32(demo+16)!=3)goto fail;
            for(unsigned i=20;i<64;i++)if(demo[i])goto fail;
            const unsigned levels[3]={0,2,8};
            for(unsigned i=0;i<3;i++) {
                const uint8_t *row=demo+64+i*168;unsigned n=get32(row+4);
                if(get32(row)!=levels[i] || !n || n>80 || row[8+(n-1)*2]!=255 || row[9+(n-1)*2]!=255)goto fail;
                for(unsigned j=0;j+1<n;j++)if(row[8+j*2]==255 && row[9+j*2]==255)goto fail;
                for(unsigned j=8+n*2;j<168;j++)if(row[j])goto fail;
            }
        }
        art->sound_test=malloc(sound_size);if(!art->sound_test)goto fail;memcpy(art->sound_test,p,sound_size);p+=sound_size;
        if(version>=8)art->debug_menu=art->sound_test+SOUND_TEST_BYTES;
        if(version>=9)art->native_sound_catalog=art->sound_test+SOUND_TEST_BYTES+DEBUG_MENU_BYTES;
        if(version>=10)art->attract=art->sound_test+SOUND_TEST_BYTES+DEBUG_MENU_BYTES+NATIVE_SOUND_CATALOG_BYTES;
    }
    if(p!=data+size)goto fail;
    return art;
fail:
    TlkFinalArtFree(art);return NULL;
}
void TlkFinalArtFree(TlkFinalArt *art) {
    if(!art)return;
    for(unsigned i=0;i<art->count;i++)free(art->images[i].pixels);
    if(art->plan)for(unsigned i=0;i<3;i++)free(art->plan->programs[i].steps);
    free(art->plan);free(art->title);TlkOptionsArtFree(art->options);TlkTitleOpeningArtFree(art->opening);
    free(art->sound_test);free(art->publisher);free(art->images);memset(art,0,sizeof *art);free(art);
}
static const FinalImage *find(const TlkFinalArt *art,uint32_t frame) {
    if(art)for(unsigned i=0;i<art->count;i++)if(art->images[i].frame==frame)return art->images+i;
    return NULL;
}
int TlkFinalArtBounds(const TlkFinalArt *art,uint32_t frame,int *x,int *y,int *w,int *h) {
    const FinalImage *image=find(art,frame);if(!image || !x || !y || !w || !h)return 0;
    *x=image->x;*y=image->y;*w=image->w;*h=image->h;return 1;
}
int TlkFinalArtPixel(const TlkFinalArt *art,uint32_t frame,int x,int y) {
    const FinalImage *image=find(art,frame);if(!image)return -1;
    int64_t dx=(int64_t)x-image->x,dy=(int64_t)y-image->y;
    if(dx<0 || dy<0 || dx>=image->w || dy>=image->h)return 0;
    return image->pixels[(size_t)dy*image->w+(size_t)dx];
}
int TlkFinalArtColor(const TlkFinalArt *art,unsigned bank,unsigned index,uint16_t *rgb555) {
    if(!art || !rgb555 || bank>3 || index>15)return 0;
    *rgb555=art->palette[bank*16+index];return 1;
}
int TlkFinalArtDrawOptions(const TlkFinalArt *art,unsigned selected,unsigned bob_x,
    unsigned difficulty,unsigned music,unsigned effects,const char buttons[3],uint32_t *out) {
    return art && TlkOptionsArtDrawBindings(art->options,selected,bob_x,difficulty,music,effects,buttons,out);
}
int TlkFinalArtSoundTestProgram(const TlkFinalArt *art,unsigned selected,unsigned *program) {
    if(!art || !art->sound_test || !program || selected>=16)return 0;
    const uint8_t *p=art->sound_test+32+320*224+selected*18;*program=p[0]|(unsigned)p[1]<<8;return 1;
}
int TlkFinalArtDrawSoundTest(const TlkFinalArt *art,unsigned selected,unsigned bob_x,uint32_t *out) {
    return art && art->sound_test && TlkOptionsArtDrawSoundTest(art->options,art->sound_test+32,art->sound_test+32+320*224,selected,bob_x,out);
}
int TlkFinalArtSoundTestName(const TlkFinalArt *art,int md,unsigned selected,char name[21]) {
    if(!art || !name || selected>=16 || (md?!art->sound_test:!art->native_sound_catalog))return 0;
    memset(name,' ',20);name[20]=0;
    const uint8_t *source=md?art->sound_test+32+320*224+selected*18+2:art->native_sound_catalog+64+selected*20;
    memcpy(name,source,md?16:20);return 1;
}
int TlkFinalArtDrawSoundTestCatalog(const TlkFinalArt *art,int md,unsigned selected,unsigned bob_x,uint32_t *out) {
    if(md)return TlkFinalArtDrawSoundTest(art,selected,bob_x,out);
    if(!art || !art->sound_test || selected>=16)return 0;
    char names[7][21];memset(names,0,sizeof names);
    for(int row=0;row<7;row++) {
        int index=(int)selected+row-3;
        if(index>=0 && index<16 && !TlkFinalArtSoundTestName(art,0,(unsigned)index,names[row]))return 0;
    }
    return TlkOptionsArtDrawSoundTestRows(art->options,art->sound_test+32,names,bob_x,out);
}
int TlkFinalArtDrawDebugMenu(const TlkFinalArt *art,unsigned selected,unsigned bob_x,
    unsigned invincible,unsigned level,uint32_t *out) {
    return art && art->debug_menu && TlkOptionsArtDrawDebugMenu(art->options,art->debug_menu+32,
        art->debug_menu+32+320*224,selected,bob_x,invincible,level,out);
}
int TlkFinalArtDrawReadyTitle(const TlkFinalArt *art,unsigned selected,unsigned bob_x,uint32_t *out) {
    if(!art || !art->title || !out || selected>1 || bob_x<118 || bob_x>128)return 0;
    const ReadyTitleArt *title=art->title;uint32_t colors[64];
    for(unsigned i=0;i<64;i++) {
        uint16_t c=title->palette[i];colors[i]=0xff000000u;
        for(unsigned j=0;j<3;j++){unsigned v=(c>>(j*5))&31;colors[i]|=((v<<3)|(v>>2))<<((2-j)*8);}
    }
    for(unsigned i=0;i<320*224;i++)out[i]=colors[title->base[i]&63];
    for(unsigned y=0;y<24;y++)for(unsigned x=0;x<24;x++) {
        unsigned index=title->selector[y*24+x];
        unsigned at=(128-8+selected*16+y)*320+bob_x-11+x;
        /* Original SAT submits the sun before Simba: sprite order wins
         * before priority is tested against planes. The prepared title
         * base also contains later sprites, so its high bit cannot mask it. */
        if(index)out[at]=colors[32+index];
    }
    return 1;
}
int TlkFinalArtAnimation(const TlkFinalArt *art,unsigned which,uint64_t updates,uint32_t *frame) {
    if(!art || !art->plan || which>2 || !frame)return 0;
    const FinalProgram *program=art->plan->programs+which;
    unsigned prefix=0,cycle=0;
    for(unsigned i=0;i<program->count;i++) {
        if(i<program->loop)prefix+=program->steps[i].ticks;
        else cycle+=program->steps[i].ticks;
    }
    if(updates>=prefix)updates=prefix+(updates-prefix)%cycle;
    for(unsigned i=0;i<program->count;i++) {
        if(updates<program->steps[i].ticks){*frame=program->steps[i].frame;return 1;}
        updates-=program->steps[i].ticks;
    }
    return 0;
}
int TlkFinalArtDrawTitleBackdrop(const TlkFinalArt *art,uint32_t *out){
    return art && TlkTitleOpeningArtBackdrop(art->opening,out);
}
int TlkFinalArtDrawTitleOpening(const TlkFinalArt *art,unsigned age,uint32_t *out){
    return art && TlkTitleOpeningArtDraw(art->opening,age,out);
}
static int draw_image(const TlkFinalArt *art,uint32_t frame,int x,int y,unsigned bank,uint32_t *out) {
    const FinalImage *image=find(art,frame);if(!image)return 0;
    for(int py=0;py<image->h;py++)for(int px=0;px<image->w;px++) {
        int dx=x+image->x+px,dy=y+image->y+py;
        if(dx<0 || dx>=320 || dy<0 || dy>=224)continue;
        unsigned index=image->pixels[(size_t)py*image->w+px];if(!index)continue;
        uint16_t c=art->palette[bank*16+index];uint32_t rgb=0xff000000u;
        for(unsigned i=0;i<3;i++) {unsigned v=c>>(i*5)&31;rgb|=((v<<3)|(v>>2))<<((2-i)*8);}
        out[dy*320+dx]=rgb;
    }
    return 1;
}
static int draw_menu_clocks(const TlkFinalArt *art,unsigned rafiki_program,
    uint64_t rafiki_updates,uint64_t icon_updates,unsigned credits,unsigned selected_no,unsigned width,uint32_t *out) {
    if(!art || !art->plan || !out || credits>9 || selected_no>1 || rafiki_program>1 || (width!=256 && width!=320))return 0;
    uint32_t rafiki,icon;
    if(!TlkFinalArtAnimation(art,rafiki_program,rafiki_updates,&rafiki) ||
       !TlkFinalArtAnimation(art,2,icon_updates,&icon))return 0;
    const FinalPlan *p=art->plan;
    int right_offset=((int)width-320)/2;
    for(unsigned i=0;i<320*224;i++)out[i]=0xff000000u;
    if(!draw_image(art,p->slots[credits?0:1],0,0,p->banks[0],out) ||
       !draw_image(art,rafiki,0,p->coordinates[0],p->banks[1],out))return 0;
    if(credits && (!draw_image(art,p->slots[2],p->coordinates[selected_no?2:1],p->coordinates[3],p->banks[2],out) ||
       !draw_image(art,icon,p->coordinates[4]+right_offset,p->coordinates[5],p->banks[3],out) ||
       !draw_image(art,p->slots[3+credits],p->coordinates[6]+right_offset,p->coordinates[7],p->banks[4],out)))return 0;
    return 1;
}
int TlkFinalArtDrawMenuClocks(const TlkFinalArt *art,unsigned rafiki_program,
    uint64_t rafiki_updates,uint64_t icon_updates,unsigned credits,unsigned selected_no,uint32_t *out) {
    return draw_menu_clocks(art,rafiki_program,rafiki_updates,icon_updates,credits,selected_no,320,out);
}
int TlkFinalArtDrawMenu(const TlkFinalArt *art,uint32_t age,unsigned credits,unsigned selected_no,uint32_t *out) {
    return TlkFinalArtDrawMenuClocks(art,0,age>=124?age-124:0,
        age>=124?age-124:0,credits,selected_no,out);
}
static int draw_confirmed_menu(const TlkFinalArt *art,uint32_t age,
    uint32_t confirmed_age,unsigned credits,unsigned width,uint32_t *out) {
    if(age<confirmed_age || confirmed_age<124 || !credits)return 0;
    uint64_t elapsed=(uint64_t)age-confirmed_age;
    /* Original 1D6AB2..1D6B10 waits for the confirmation sound before actor
     * updates resume. Submitted sprites become visible two fields later.
     * The icon retains its pre-confirmation timer; Rafiki starts exit script1. */
    uint64_t idle=confirmed_age-124;
    return draw_menu_clocks(art,elapsed>=59?1:0,
        elapsed>=59?elapsed-59:idle,idle+(elapsed>=57?elapsed-57:0),credits,0,width,out);
}
int TlkFinalArtDrawConfirmedMenu(const TlkFinalArt *art,uint32_t age,
    uint32_t confirmed_age,unsigned credits,uint32_t *out) {
    return draw_confirmed_menu(art,age,confirmed_age,credits,320,out);
}
int TlkFinalArtDrawMenuViewport(const TlkFinalArt *art,uint32_t age,
    unsigned credits,unsigned selected_no,unsigned width,uint32_t *out) {
    return draw_menu_clocks(art,0,age>=124?age-124:0,
        age>=124?age-124:0,credits,selected_no,width,out);
}
int TlkFinalArtDrawConfirmedMenuViewport(const TlkFinalArt *art,uint32_t age,
    uint32_t confirmed_age,unsigned credits,unsigned width,uint32_t *out) {
    return draw_confirmed_menu(art,age,confirmed_age,credits,width,out);
}
