/* Explicit little-endian installed images; no guest/ROM memory in playback. */
enum { CAP_HEADER=192,CAP_LIMIT=131072 };
static const uint8_t cap_snes[32]={0x45,0x7a,0xbe,0x63,0x4e,0x0a,0x8b,0xe0,0x3e,0x29,0x51,0x3a,0x3d,0xca,0x8f,0x3e,0x9d,0x0d,0xdc,0x6b,0xf9,0x7d,0x89,0x31,0xf2,0x31,0x60,0x94,0x26,0x0f,0x37,0x12};
static const uint8_t cap_md[32]={0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
static uint32_t cap_get(const uint8_t *p) {return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void cap_put(uint8_t *p,uint32_t v) {for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
TlkTitleArt *TlkTitleArtLoad(const uint8_t *p,size_t size) {
    if(!p || size<CAP_HEADER+64+32 || size>CAP_LIMIT || memcmp(p,"TLKCAP01",8) ||
       (cap_get(p+8)!=1 && cap_get(p+8)!=2) || cap_get(p+12)!=CAP_HEADER || cap_get(p+16)!=size || cap_get(p+20)!=2 ||
       memcmp(p+24,cap_snes,32) || memcmp(p+56,cap_md,32))return NULL;
    unsigned version=cap_get(p+8);
    if(cap_get(p+120)!=(version==2?CAPTION_COUNT:0))return NULL;
    for(unsigned i=124;i<CAP_HEADER;i++)if(p[i])return NULL;
    uint8_t hash[32];sha256_compute(p+CAP_HEADER,size-CAP_HEADER,hash);if(memcmp(hash,p+88,32))return NULL;
    TlkTitleArt *art=calloc(1,sizeof *art);if(!art)return NULL;size_t at=CAP_HEADER;
    for(unsigned bank=0;bank<2;bank++)for(unsigned i=0;i<16;i++) {
        uint16_t c=(uint16_t)(p[at]|(unsigned)p[at+1]<<8);at+=2;
        if(c&0x8000)goto fail;(bank?art->md:art->native)[i]=c;
    }
    for(unsigned source=0;source<2;source++) {
        if(at>size || size-at<16)goto fail;
        int *g=art->geometry[source];
        g[0]=(int32_t)cap_get(p+at);g[1]=(int32_t)cap_get(p+at+4);
        uint32_t w=cap_get(p+at+8),h=cap_get(p+at+12);at+=16;
        if(g[0]<-256 || g[0]>0 || g[1]<-128 || g[1]>128 || !w || w>512 || !h || h>64)goto fail;
        size_t area=(size_t)w*h;if(area>size-at)goto fail;g[2]=(int)w;g[3]=(int)h;
        for(size_t i=0;i<area;i++)if(p[at+i]>15)goto fail;
        art->pixels[source]=malloc(area);if(!art->pixels[source])goto fail;
        memcpy(art->pixels[source],p+at,area);at+=area;
    }
    if(version==2)for(unsigned i=0;i<CAPTION_COUNT;i++) {
        if(at>size || size-at<32)goto fail;CaptionImage *c=&art->captions[i];
        c->level=cap_get(p+at);c->hint=cap_get(p+at+4);c->count=cap_get(p+at+8);c->frame=cap_get(p+at+12);
        c->geometry[0]=(int32_t)cap_get(p+at+16);c->geometry[1]=(int32_t)cap_get(p+at+20);
        unsigned w=cap_get(p+at+24),h=cap_get(p+at+28);at+=32;
        if(c->level!=(i==14?1:i) || c->hint!=(i==14) || c->frame!=caption_frames[i] ||
           !c->count || c->count>CAPTION_GLYPHS || c->geometry[0]<-256 || c->geometry[0]>0 ||
           c->geometry[1]<-128 || c->geometry[1]>128 || !w || w>512 || !h || h>64 ||
           size-at<c->count*6)goto fail;
        c->geometry[2]=(int)w;c->geometry[3]=(int)h;
        for(unsigned j=0;j<c->count;j++)for(unsigned k=0;k<3;k++) {
            c->glyphs[j][k]=(uint16_t)(p[at]|(unsigned)p[at+1]<<8);at+=2;
        }
        for(unsigned j=0;j<c->count;j++) {
            unsigned g=c->glyphs[j][2];
            if(c->glyphs[j][0]>496 || c->glyphs[j][1]>48 || g<0x88ef ||
               (g-0x88ef)%128 || ((g-0x88ef)/128>=26 && (g-0x88ef)/128!=37))goto fail;
        }
        size_t area=(size_t)w*h;if(area>size-at)goto fail;
        for(size_t j=0;j<area;j++)if(p[at+j]>15)goto fail;
        c->pixels=malloc(area);if(!c->pixels)goto fail;memcpy(c->pixels,p+at,area);at+=area;
    }
    if(at!=size)goto fail;if(version==2)art->caption_count=CAPTION_COUNT;return art;
fail:TlkTitleArtFree(art);return NULL;
}
TlkTitleArt *TlkTitleArtReadFile(const char *path) {
    FILE *f=path && *path?fopen(path,"rb"):NULL;if(!f)return NULL;
    int ok=!fseek(f,0,SEEK_END);long n=ok?ftell(f):-1;
    ok=ok && n>=CAP_HEADER && n<=CAP_LIMIT && !fseek(f,0,SEEK_SET);
    uint8_t *p=ok?malloc((size_t)n):NULL;ok=ok && p && fread(p,1,(size_t)n,f)==(size_t)n && fgetc(f)==EOF;
    if(fclose(f))ok=0;TlkTitleArt *art=ok?TlkTitleArtLoad(p,(size_t)n):NULL;free(p);return art;
}
#ifdef TLK_TITLE_ART_PREPARE
int TlkTitleArtPrepare(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms,uint8_t **record,size_t *size) {
    if(record)*record=NULL;if(size)*size=0;if(!record || !size)return 0;
    TlkTitleArt *art=TlkTitleArtCreate(snes,ss,md,ms);if(!art)return 0;
    int g[2][4];size_t total=CAP_HEADER+64+32;
    for(unsigned s=0;s<2;s++) {
        if(!TlkTitleArtBounds(art,s,&g[s][0],&g[s][1],&g[s][2],&g[s][3])) {TlkTitleArtFree(art);return 0;}
        total+=(size_t)g[s][2]*g[s][3];
    }
    if(!TlkTitleArtCaptionsReady(art)){TlkTitleArtFree(art);return 0;}
    for(unsigned i=0;i<CAPTION_COUNT;i++) {
        const CaptionImage *c=&art->captions[i];
        total+=32+c->count*6+(size_t)c->geometry[2]*c->geometry[3];
    }
    if(total>CAP_LIMIT){TlkTitleArtFree(art);return 0;}
    uint8_t *p=calloc(1,total);if(!p){TlkTitleArtFree(art);return 0;}
    memcpy(p,"TLKCAP01",8);cap_put(p+8,2);cap_put(p+12,CAP_HEADER);cap_put(p+16,(uint32_t)total);cap_put(p+20,2);
    cap_put(p+120,CAPTION_COUNT);
    memcpy(p+24,cap_snes,32);memcpy(p+56,cap_md,32);size_t at=CAP_HEADER;
    for(unsigned bank=0;bank<2;bank++)for(unsigned i=0;i<16;i++) {
        uint16_t c=(bank?art->md:art->native)[i];p[at++]=(uint8_t)c;p[at++]=(uint8_t)(c>>8);
    }
    for(unsigned s=0;s<2;s++) {
        for(unsigned i=0;i<4;i++){cap_put(p+at,(uint32_t)g[s][i]);at+=4;}
        for(int y=0;y<g[s][3];y++)for(int x=0;x<g[s][2];x++)p[at++]=(uint8_t)TitlePixel(art,g[s][0]+x,g[s][1]+y,s);
    }
    for(unsigned i=0;i<CAPTION_COUNT;i++) {
        const CaptionImage *c=&art->captions[i];
        cap_put(p+at,c->level);cap_put(p+at+4,c->hint);cap_put(p+at+8,c->count);cap_put(p+at+12,c->frame);at+=16;
        for(unsigned j=0;j<4;j++){cap_put(p+at,(uint32_t)c->geometry[j]);at+=4;}
        for(unsigned j=0;j<c->count;j++)for(unsigned k=0;k<3;k++) {
            unsigned v=c->glyphs[j][k];p[at++]=(uint8_t)v;p[at++]=(uint8_t)(v>>8);
        }
        size_t area=(size_t)c->geometry[2]*c->geometry[3];memcpy(p+at,c->pixels,area);at+=area;
    }
    if(at!=total){TlkTitleArtFree(art);free(p);return 0;}
    sha256_compute(p+CAP_HEADER,total-CAP_HEADER,p+88);TlkTitleArtFree(art);
    TlkTitleArt *checked=TlkTitleArtLoad(p,total);if(!checked){free(p);return 0;}TlkTitleArtFree(checked);
    *record=p;*size=total;return 1;
}
#endif
