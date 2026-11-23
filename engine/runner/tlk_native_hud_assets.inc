enum { NH_HEADER=112,NH_TOTAL=NH_HEADER+FONT_SIZE };
static const uint8_t nh_source[32]={0x45,0x7a,0xbe,0x63,0x4e,0x0a,0x8b,0xe0,0x3e,0x29,0x51,0x3a,0x3d,0xca,0x8f,0x3e,0x9d,0x0d,0xdc,0x6b,0xf9,0x7d,0x89,0x31,0xf2,0x31,0x60,0x94,0x26,0x0f,0x37,0x12};
static uint32_t nh_get(const uint8_t *p) {return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
#ifdef TLK_NATIVE_HUD_PREPARE
static void nh_put(uint8_t *p,uint32_t v) {for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
#endif
TlkNativeHud *TlkNativeHudLoad(const uint8_t *p,size_t size) {
    if(!p || size!=NH_TOTAL || memcmp(p,"TLKNHUD1",8) || nh_get(p+8)!=1 || nh_get(p+12)!=NH_HEADER ||
       nh_get(p+16)!=size || nh_get(p+20)!=FONT_SIZE || memcmp(p+24,nh_source,32))return NULL;
    for(unsigned i=88;i<NH_HEADER;i++)if(p[i])return NULL;
    uint8_t hash[32];sha256_compute(p+NH_HEADER,FONT_SIZE,hash);if(memcmp(hash,p+56,32))return NULL;
    TlkNativeHud *hud=malloc(sizeof *hud);if(!hud)return NULL;
    hud->ready=READY;memcpy(hud->font,p+NH_HEADER,FONT_SIZE);return hud;
}
TlkNativeHud *TlkNativeHudReadFile(const char *path) {
    FILE *f=path && *path?fopen(path,"rb"):NULL;if(!f)return NULL;
    uint8_t p[NH_TOTAL];int ok=fread(p,1,sizeof p,f)==sizeof p && fgetc(f)==EOF;
    if(fclose(f))ok=0;return ok?TlkNativeHudLoad(p,sizeof p):NULL;
}
#ifdef TLK_NATIVE_HUD_PREPARE
int TlkNativeHudPrepare(const uint8_t *rom,size_t bytes,uint8_t **record,size_t *size) {
    if(record)*record=NULL;if(size)*size=0;if(!record || !size)return 0;
    TlkNativeHud *hud=TlkNativeHudCreate(rom,bytes);if(!hud)return 0;
    uint8_t *p=calloc(1,NH_TOTAL);if(!p){TlkNativeHudFree(hud);return 0;}
    memcpy(p,"TLKNHUD1",8);nh_put(p+8,1);nh_put(p+12,NH_HEADER);nh_put(p+16,NH_TOTAL);nh_put(p+20,FONT_SIZE);
    memcpy(p+24,nh_source,32);memcpy(p+NH_HEADER,hud->font,FONT_SIZE);sha256_compute(p+NH_HEADER,FONT_SIZE,p+56);
    TlkNativeHudFree(hud);*record=p;*size=NH_TOTAL;return 1;
}
#endif
