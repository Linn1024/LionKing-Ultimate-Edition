/* Included after the reviewed renderer/map, in installer and playback clones.
 * Explicit fields bind the map policy; no pointer-bearing C structs are stored. */
#include "sha256.h"
#include "tlk_pride_data.h"
#include "tlk_hitbox_data.h"
enum { SP_HEADER=192, SP_LIMIT=32*1024*1024, SP_PALETTES=416, SP_BANK=17792 };
static const uint8_t sp_snes[32]={0x45,0x7a,0xbe,0x63,0x4e,0x0a,0x8b,0xe0,0x3e,0x29,0x51,0x3a,0x3d,0xca,0x8f,0x3e,
    0x9d,0x0d,0xdc,0x6b,0xf9,0x7d,0x89,0x31,0xf2,0x31,0x60,0x94,0x26,0x0f,0x37,0x12};
static const uint8_t sp_md[32]={0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,
    0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
static uint32_t sp_u32(const uint8_t *p){return p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void sp_put(uint8_t *p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static unsigned sp_deaths(void){return sizeof cub_death_poses/sizeof cub_death_poses[0];}
static int sp_policy(uint8_t out[32]){
    size_t hitbox_policy=TlkHitboxDataPolicySize();
    size_t size=12+hitbox_policy+(size_t)COUNT*840+sizeof cub_death_poses;
    uint8_t *data=malloc(size);if(!data)return 0;size_t at=0;
#define SP_NUMBER(value) do{sp_put(data+at,(uint32_t)(value));at+=4;}while(0)
    SP_NUMBER(COUNT);SP_NUMBER(sp_deaths());SP_NUMBER(142); /* Complete first adult hyena taunt drawings. */
    if(!TlkHitboxDataPolicyWrite(data+at,hitbox_policy)){free(data);return 0;}at+=hitbox_policy;
    for(unsigned i=0;i<COUNT;i++){
        const struct SpriteMap *m=&sprite_map[i];
        SP_NUMBER(m->snes);SP_NUMBER(m->md);SP_NUMBER(m->x);SP_NUMBER(m->y);SP_NUMBER(m->w);SP_NUMBER(m->h);
        SP_NUMBER(m->extra_count);SP_NUMBER(m->role);SP_NUMBER(m->native_palette);SP_NUMBER(m->md_palette);
        for(unsigned j=0;j<64;j++){SP_NUMBER(m->extra[j].x);SP_NUMBER(m->extra[j].y);SP_NUMBER(m->extra[j].c);}
        memcpy(data+at,m->md_to_native,16);at+=16;memcpy(data+at,m->native_to_md,16);at+=16;
    }
    for(unsigned i=0;i<sp_deaths();i++)SP_NUMBER(cub_death_poses[i]);
#undef SP_NUMBER
    int ok=at==size;if(ok)sha256_compute(data,size,out);free(data);return ok;
}
static int sp_valid(const uint8_t *p,size_t size){
    if(!p || size<SP_HEADER+SP_PALETTES+SP_BANK || size>SP_LIMIT || memcmp(p,"TLKSPR01",8) ||
       sp_u32(p+8)!=2 || sp_u32(p+12)!=SP_HEADER || sp_u32(p+16)!=size || sp_u32(p+20)!=COUNT ||
       memcmp(p+24,sp_snes,32) || memcmp(p+56,sp_md,32) || sp_u32(p+152)!=SP_BANK ||
       sp_u32(p+156)!=sp_deaths() || sp_u32(p+160)!=COUNT)return 0;
    unsigned gameplay=sp_u32(p+164);if(!gameplay || gameplay>size)return 0;
    for(unsigned i=168;i<SP_HEADER;i++)if(p[i])return 0;
    uint8_t hash[32];if(!sp_policy(hash) || memcmp(hash,p+88,32))return 0;
    sha256_compute(p+SP_HEADER,size-SP_HEADER,hash);if(memcmp(hash,p+120,32))return 0;
    size_t at=SP_HEADER+SP_PALETTES+SP_BANK;unsigned deaths=0;
    for(unsigned i=0;i<COUNT;i++){
        const struct SpriteMap *m=&sprite_map[i];
        if(m->w<=0 || m->h<=0 || m->w>256 || m->h>256 || size-at<12)return 0;
        unsigned area=(unsigned)m->w*m->h,a=sp_u32(p+at+4),b=sp_u32(p+at+8);int death=TlkMdSpritesCubDeathPose(m->snes);
        if(sp_u32(p+at)!=m->snes || a!=area || b!=(death?area:0))return 0;at+=12;
        if(a>size-at || b>size-at-a)return 0;
        for(size_t j=0;j<(size_t)a+b;j++)if(p[at+j]>15)return 0;
        if(death){if(memcmp(p+at,p+at+a,area))return 0;deaths++;}
        at+=(size_t)a+b;
    }
    return gameplay==size-at && deaths==sp_deaths() && TlkPrideDataRead(p+at,gameplay,0);
}
