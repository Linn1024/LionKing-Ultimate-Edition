/* Three original-equal SNES/MD image pairs, stored once; palettes independent. */
enum { CK_HEADER=192,CK_LIMIT=131072 };
static const uint8_t ck_snes[32]={0x45,0x7a,0xbe,0x63,0x4e,0x0a,0x8b,0xe0,0x3e,0x29,0x51,0x3a,0x3d,0xca,0x8f,0x3e,0x9d,0x0d,0xdc,0x6b,0xf9,0x7d,0x89,0x31,0xf2,0x31,0x60,0x94,0x26,0x0f,0x37,0x12};
static const uint8_t ck_md[32]={0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
static uint32_t ck_get(const uint8_t *p) {return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void ck_put(uint8_t *p,uint32_t v) {for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
TlkCheckpointArt *TlkCheckpointArtLoad(const uint8_t *p,size_t size) {
    if(!p || size<CK_HEADER+64+60 || size>CK_LIMIT || memcmp(p,"TLKCHK01",8) || ck_get(p+8)!=1 ||
       ck_get(p+12)!=CK_HEADER || ck_get(p+16)!=size || ck_get(p+20)!=3 ||
       memcmp(p+24,ck_snes,32) || memcmp(p+56,ck_md,32))return NULL;
    for(unsigned i=120;i<CK_HEADER;i++)if(p[i])return NULL;
    uint8_t hash[32];sha256_compute(p+CK_HEADER,size-CK_HEADER,hash);if(memcmp(hash,p+88,32))return NULL;
    TlkCheckpointArt *art=calloc(1,sizeof *art);if(!art)return NULL;size_t at=CK_HEADER;
    for(unsigned bank=0;bank<2;bank++)for(unsigned i=0;i<16;i++) {
        uint16_t c=(uint16_t)(p[at]|(unsigned)p[at+1]<<8);at+=2;
        if(c&0x8000)goto fail;(bank?art->md:art->native)[i]=c;
    }
    for(unsigned i=0;i<3;i++) {
        if(at>size || size-at<20 || ck_get(p+at)!=checkpoint_poses[i])goto fail;at+=4;
        int *g=art->geometry[i];g[0]=(int32_t)ck_get(p+at);g[1]=(int32_t)ck_get(p+at+4);
        uint32_t w=ck_get(p+at+8),h=ck_get(p+at+12);at+=16;
        if(g[0]<-192 || g[0]>192 || g[1]<-192 || g[1]>192 || !w || w>128 || !h || h>128)goto fail;
        size_t area=(size_t)w*h;if(area>size-at)goto fail;g[2]=(int)w;g[3]=(int)h;
        for(size_t j=0;j<area;j++)if(p[at+j]>15)goto fail;
        art->pixels[i]=malloc(area);if(!art->pixels[i])goto fail;
        memcpy(art->pixels[i],p+at,area);at+=area;
    }
    if(at!=size)goto fail;return art;
fail:TlkCheckpointArtFree(art);return NULL;
}
TlkCheckpointArt *TlkCheckpointArtReadFile(const char *path) {
    FILE *f=path && *path?fopen(path,"rb"):NULL;if(!f)return NULL;
    int ok=!fseek(f,0,SEEK_END);long n=ok?ftell(f):-1;
    ok=ok && n>=CK_HEADER && n<=CK_LIMIT && !fseek(f,0,SEEK_SET);
    uint8_t *p=ok?malloc((size_t)n):NULL;ok=ok && p && fread(p,1,(size_t)n,f)==(size_t)n && fgetc(f)==EOF;
    if(fclose(f))ok=0;TlkCheckpointArt *art=ok?TlkCheckpointArtLoad(p,(size_t)n):NULL;free(p);return art;
}
#ifdef TLK_CHECKPOINT_ART_PREPARE
int TlkCheckpointArtPrepare(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms,uint8_t **record,size_t *size) {
    if(record)*record=NULL;if(size)*size=0;if(!record || !size)return 0;
    TlkCheckpointArt *art=TlkCheckpointArtCreate(snes,ss,md,ms);if(!art)return 0;
    int g[3][4];size_t total=CK_HEADER+64+60;
    for(unsigned i=0;i<3;i++) {
        if(!TlkCheckpointArtPoseBounds(art,checkpoint_poses[i],&g[i][0],&g[i][1],&g[i][2],&g[i][3])) {TlkCheckpointArtFree(art);return 0;}
        total+=(size_t)g[i][2]*g[i][3];
    }
    if(total>CK_LIMIT){TlkCheckpointArtFree(art);return 0;}
    uint8_t *p=calloc(1,total);if(!p){TlkCheckpointArtFree(art);return 0;}
    memcpy(p,"TLKCHK01",8);ck_put(p+8,1);ck_put(p+12,CK_HEADER);ck_put(p+16,(uint32_t)total);ck_put(p+20,3);
    memcpy(p+24,ck_snes,32);memcpy(p+56,ck_md,32);size_t at=CK_HEADER;
    for(unsigned bank=0;bank<2;bank++)for(unsigned i=0;i<16;i++) {
        uint16_t c=(bank?art->md:art->native)[i];p[at++]=(uint8_t)c;p[at++]=(uint8_t)(c>>8);
    }
    for(unsigned i=0;i<3;i++) {
        ck_put(p+at,checkpoint_poses[i]);at+=4;
        for(unsigned j=0;j<4;j++){ck_put(p+at,(uint32_t)g[i][j]);at+=4;}
        for(int y=0;y<g[i][3];y++)for(int x=0;x<g[i][2];x++)p[at++]=(uint8_t)TlkCheckpointArtPosePixel(art,checkpoint_poses[i],g[i][0]+x,g[i][1]+y,0);
    }
    sha256_compute(p+CK_HEADER,total-CK_HEADER,p+88);TlkCheckpointArtFree(art);
    TlkCheckpointArt *checked=TlkCheckpointArtLoad(p,total);if(!checked){free(p);return 0;}TlkCheckpointArtFree(checked);
    *record=p;*size=total;return 1;
}
#endif
