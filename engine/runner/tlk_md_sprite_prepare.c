/* Installer-only use of the unchanged reviewed ROM renderer/decoder. */
#include "tlk_md_sprites.c"
#include "tlk_md_sprite_prepare.h"
#include "tlk_md_sprite_format.inc"
int TlkMdSpriteAssetsPrepare(const uint8_t *snes,size_t snes_size,const uint8_t *md,size_t md_size,
                            uint8_t **record,size_t *record_size){
    if(record)*record=NULL;if(record_size)*record_size=0;
    if(!record || !record_size || !snes || !md || snes_size!=0x300000 || md_size!=0x300000)return 0;
    uint8_t hash[32];sha256_compute(snes,snes_size,hash);if(memcmp(hash,sp_snes,32))return 0;
    sha256_compute(md,md_size,hash);if(memcmp(hash,sp_md,32))return 0;
    unsigned loaded=TlkMdSpritesInit(md,md_size);TlkMdSpritesBindSnes(snes,snes_size);
    if(loaded!=COUNT || native_death_count!=sp_deaths() || native_death_size!=SP_BANK){TlkMdSpritesClear();return 0;}
    if(!TlkPrideDataPrepare(snes,snes_size,md,md_size)){TlkMdSpritesClear();return 0;}
    size_t gameplay=TlkPrideDataRecordSize(),total=SP_HEADER+SP_PALETTES+SP_BANK+gameplay;
    for(unsigned i=0;i<COUNT;i++)total+=12+(size_t)sprite_map[i].w*sprite_map[i].h*(native_death_images[i]?2:1);
    if(total>SP_LIMIT){TlkMdSpritesClear();return 0;}
    uint8_t *p=calloc(1,total);if(!p){TlkMdSpritesClear();return 0;}
    memcpy(p,"TLKSPR01",8);sp_put(p+8,2);sp_put(p+12,SP_HEADER);sp_put(p+16,(uint32_t)total);sp_put(p+20,COUNT);
    memcpy(p+24,sp_snes,32);memcpy(p+56,sp_md,32);
    if(!sp_policy(p+88)){free(p);TlkMdSpritesClear();return 0;}
    sp_put(p+152,SP_BANK);sp_put(p+156,sp_deaths());sp_put(p+160,loaded);
    sp_put(p+164,(uint32_t)gameplay);
    size_t at=SP_HEADER;
    for(unsigned i=0;i<128;i++){unsigned c=native_palettes[i/16][i%16];p[at++]=(uint8_t)c;p[at++]=(uint8_t)(c>>8);}
    for(unsigned i=0;i<64;i++){unsigned c=md_palettes[i/16][i%16];p[at++]=(uint8_t)c;p[at++]=(uint8_t)(c>>8);}
    for(unsigned i=0;i<16;i++){unsigned c=TlkMdColor555(be16(md+0x1d78aa+i*2));p[at++]=(uint8_t)c;p[at++]=(uint8_t)(c>>8);}
    memcpy(p+at,native_death_bank,SP_BANK);at+=SP_BANK;
    for(unsigned i=0;i<COUNT;i++){
        unsigned area=(unsigned)sprite_map[i].w*sprite_map[i].h;
        sp_put(p+at,sprite_map[i].snes);sp_put(p+at+4,area);sp_put(p+at+8,native_death_images[i]?area:0);at+=12;
        memcpy(p+at,images[i],area);at+=area;
        if(native_death_images[i]){memcpy(p+at,native_death_images[i],area);at+=area;}
    }
    if(!TlkPrideDataWrite(p+at,gameplay)){free(p);TlkMdSpritesClear();return 0;}at+=gameplay;
    sha256_compute(p+SP_HEADER,total-SP_HEADER,p+120);TlkMdSpritesClear();
    if(at!=total || !sp_valid(p,total)){free(p);return 0;}
    *record=p;*record_size=total;return 1;
}
