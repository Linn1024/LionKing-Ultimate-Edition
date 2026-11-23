/* Thirteen original-equal source image pairs, with owned prepared playback. */
enum { REV_HEADER=192,REV_LIMIT=2*1024*1024 };
static const uint8_t rev_snes[32]={0x45,0x7a,0xbe,0x63,0x4e,0x0a,0x8b,0xe0,0x3e,0x29,0x51,0x3a,0x3d,0xca,0x8f,0x3e,0x9d,0x0d,0xdc,0x6b,0xf9,0x7d,0x89,0x31,0xf2,0x31,0x60,0x94,0x26,0x0f,0x37,0x12};
static const uint8_t rev_md[32]={0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
static uint32_t rev_get(const uint8_t *p) {return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void rev_put(uint8_t *p,uint32_t v) {for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
TlkRevivalArt *TlkRevivalArtClone(const TlkRevivalArt *art) {
    if(!art || !art->count || art->count>FRAMES)return NULL;
    TlkRevivalArt *copy=calloc(1,sizeof *copy);if(!copy)return NULL;copy->count=art->count;
    for(unsigned i=0;i<art->count;i++) {
        copy->frames[i].pose=art->frames[i].pose;
        for(unsigned s=0;s<2;s++) {
            const Image *from=&art->frames[i].image[s];Image *to=&copy->frames[i].image[s];
            if(!from->pixels || from->w<=0 || from->w>256 || from->h<=0 || from->h>256)goto fail;
            *to=*from;to->pixels=malloc((size_t)from->w*from->h);if(!to->pixels)goto fail;
            memcpy(to->pixels,from->pixels,(size_t)from->w*from->h);
        }
    }
    return copy;
fail:TlkRevivalArtFree(copy);return NULL;
}
TlkRevivalArt *TlkRevivalArtLoad(const uint8_t *p,size_t size) {
    if(!p || size<REV_HEADER+FRAMES*20 || size>REV_LIMIT || memcmp(p,"TLKREV01",8) ||
       rev_get(p+8)!=1 || rev_get(p+12)!=REV_HEADER || rev_get(p+16)!=size || rev_get(p+20)!=FRAMES ||
       memcmp(p+24,rev_snes,32) || memcmp(p+56,rev_md,32))return NULL;
    for(unsigned i=120;i<REV_HEADER;i++)if(p[i])return NULL;
    uint8_t hash[32];sha256_compute(p+REV_HEADER,size-REV_HEADER,hash);if(memcmp(hash,p+88,32))return NULL;
    TlkRevivalArt *art=calloc(1,sizeof *art);if(!art)return NULL;art->count=FRAMES;size_t at=REV_HEADER;
    for(unsigned i=0;i<FRAMES;i++) {
        if(at>size || size-at<20)goto fail;
        Frame *f=&art->frames[i];f->pose=rev_get(p+at);int x=(int32_t)rev_get(p+at+4),y=(int32_t)rev_get(p+at+8);
        uint32_t w=rev_get(p+at+12),h=rev_get(p+at+16);at+=20;
        if(f->pose<0xc00000 || f->pose>=0xf00000 || x< -192 || x>192 || y< -192 || y>192 || !w || w>256 || !h || h>256)goto fail;
        size_t area=(size_t)w*h;if(area>size-at)goto fail;
        for(size_t j=0;j<area;j++)if(p[at+j]>15)goto fail;
        for(unsigned s=0;s<2;s++) {
            Image *im=&f->image[s];im->x=x;im->y=y;im->w=(int)w;im->h=(int)h;
            im->pixels=malloc(area);if(!im->pixels)goto fail;memcpy(im->pixels,p+at,area);
        }
        at+=area;
    }
    if(at!=size)goto fail;return art;
fail:TlkRevivalArtFree(art);return NULL;
}
TlkRevivalArt *TlkRevivalArtReadFile(const char *path) {
    FILE *f=path && *path?fopen(path,"rb"):NULL;if(!f)return NULL;
    int ok=!fseek(f,0,SEEK_END);long n=ok?ftell(f):-1;
    ok=ok && n>=REV_HEADER && n<=REV_LIMIT && !fseek(f,0,SEEK_SET);
    uint8_t *p=ok?malloc((size_t)n):NULL;ok=ok && p && fread(p,1,(size_t)n,f)==(size_t)n && fgetc(f)==EOF;
    if(fclose(f))ok=0;TlkRevivalArt *art=ok?TlkRevivalArtLoad(p,(size_t)n):NULL;free(p);return art;
}
#ifdef TLK_REVIVAL_ART_PREPARE
int TlkRevivalArtPrepare(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms,uint8_t **record,size_t *size) {
    if(record)*record=NULL;if(size)*size=0;if(!record || !size)return 0;
    TlkRevivalArt *art=TlkRevivalArtCreate(snes,ss,md,ms);if(!art)return 0;
    size_t total=REV_HEADER+FRAMES*20;for(unsigned i=0;i<FRAMES;i++)total+=(size_t)art->frames[i].image[0].w*art->frames[i].image[0].h;
    if(total>REV_LIMIT){TlkRevivalArtFree(art);return 0;}
    uint8_t *p=calloc(1,total);if(!p){TlkRevivalArtFree(art);return 0;}
    memcpy(p,"TLKREV01",8);rev_put(p+8,1);rev_put(p+12,REV_HEADER);rev_put(p+16,(uint32_t)total);rev_put(p+20,FRAMES);
    memcpy(p+24,rev_snes,32);memcpy(p+56,rev_md,32);size_t at=REV_HEADER;
    for(unsigned i=0;i<FRAMES;i++) {
        const Frame *f=&art->frames[i];const Image *im=&f->image[0];
        rev_put(p+at,f->pose);rev_put(p+at+4,(uint32_t)im->x);rev_put(p+at+8,(uint32_t)im->y);
        rev_put(p+at+12,(uint32_t)im->w);rev_put(p+at+16,(uint32_t)im->h);at+=20;
        size_t area=(size_t)im->w*im->h;memcpy(p+at,im->pixels,area);at+=area;
    }
    sha256_compute(p+REV_HEADER,total-REV_HEADER,p+88);TlkRevivalArtFree(art);
    TlkRevivalArt *checked=TlkRevivalArtLoad(p,total);if(!checked){free(p);return 0;}TlkRevivalArtFree(checked);
    *record=p;*size=total;return 1;
}
#endif
