/* Playback import. No ROM decode/bind or source-palette extraction is called. */
#include "tlk_md_sprite_assets.h"
#include "tlk_md_sprite_format.inc"
static uint8_t *sp_installed;
static size_t sp_installed_size;
int TlkMdSpriteAssetsLoad(const uint8_t *record,size_t size){
    if(!sp_valid(record,size))return 0;
    uint8_t *copy=malloc(size);if(!copy)return 0;memcpy(copy,record,size);
    free(sp_installed);sp_installed=copy;sp_installed_size=size;return 1;
}
int TlkMdSpriteAssetsReadFile(const char *path){
    FILE *f=path && *path?fopen(path,"rb"):NULL;if(!f)return 0;
    int ok=!fseek(f,0,SEEK_END);long length=ok?ftell(f):-1;
    ok=ok && length>=SP_HEADER && length<=SP_LIMIT && !fseek(f,0,SEEK_SET);
    uint8_t *p=ok?malloc((size_t)length):NULL;ok=ok && p && fread(p,1,(size_t)length,f)==(size_t)length && fgetc(f)==EOF;
    if(fclose(f))ok=0;if(ok)ok=TlkMdSpriteAssetsLoad(p,(size_t)length);free(p);return ok;
}
int TlkMdSpriteAssetsReady(void){return sp_installed!=NULL && sp_installed_size>=SP_HEADER;}
int TlkMdSpriteAssetsSharedPalettes(uint16_t *native,uint16_t *md){
    if(!TlkMdSpriteAssetsReady())return 0;
    for(unsigned i=0;i<16;i++){
        if(native)native[i]=(uint16_t)le16(sp_installed+SP_HEADER+i*2);
        if(md)md[i]=(uint16_t)le16(sp_installed+SP_HEADER+384+i*2);
    }
    return 1;
}
int TlkMdSpriteAssetsActivate(void){
    if(!TlkMdSpriteAssetsReady())return 0;
    uint8_t *pending[COUNT]={0},*death[COUNT]={0},*bank=malloc(SP_BANK);
    if(!bank)return 0;
    memcpy(bank,sp_installed+SP_HEADER+SP_PALETTES,SP_BANK);
    size_t at=SP_HEADER+SP_PALETTES+SP_BANK;
    for(unsigned i=0;i<COUNT;i++){
        unsigned a=sp_u32(sp_installed+at+4),b=sp_u32(sp_installed+at+8);at+=12;
        pending[i]=malloc(a);if(!pending[i])goto fail;memcpy(pending[i],sp_installed+at,a);at+=a;
        if(b){death[i]=malloc(b);if(!death[i])goto fail;memcpy(death[i],sp_installed+at,b);at+=b;}
    }
    if(!TlkPrideDataRead(sp_installed+at,sp_installed_size-at,1))goto fail;
    TlkMdSpritesClear();memcpy(images,pending,sizeof images);memcpy(native_death_images,death,sizeof native_death_images);
    native_death_bank=bank;native_death_size=SP_BANK;native_death_count=sp_deaths();native_ready=1;
    for(unsigned i=0;i<128;i++)native_palettes[i/16][i%16]=(uint16_t)le16(sp_installed+SP_HEADER+i*2);
    for(unsigned i=0;i<64;i++)md_palettes[i/16][i%16]=(uint16_t)le16(sp_installed+SP_HEADER+256+i*2);
    return 1;
fail:
    for(unsigned i=0;i<COUNT;i++){free(pending[i]);free(death[i]);}free(bank);return 0;
}
