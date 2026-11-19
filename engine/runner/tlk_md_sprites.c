#include "tlk_fallback_log.h"
#include "tlk_md_sprites.h"
#include "tlk_mixed_palette.h"
#include "tlk_md_assets.h"
#include "tlk_toss_life_palette.h"
#include "tlk_world_life_sprite.h"
#include "sha256.h"
#include "tlk_cw_rhino_metadata.h"
#include "tlk_cw_hippo_metadata.h"
#include "tlk_cw_ride_palette_metadata.h"
#include "tlk_graveyard_bone_object_metadata.h"
#include "tlk_graveyard_pillar_metadata.h"
#include "tlk_prepared_geyser_metadata.h"
#include "tlk_next_scene_data.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "pride_sprite_map.h"
enum { COUNT=sizeof sprite_map/sizeof sprite_map[0] };
static uint8_t *images[COUNT];
static uint16_t mixed_used[COUNT];
static unsigned mixed_palette_used(unsigned n) {
    if(!images[n])return 0;
    if(!mixed_used[n]) {
        unsigned mask=1;
        for(unsigned i=0;i<(unsigned)sprite_map[n].w*sprite_map[n].h;i++)mask|=1u<<(images[n][i]&15);
        mixed_used[n]=(uint16_t)mask;
    }
    return mixed_used[n];
}
static uint8_t seen[COUNT];
static unsigned missing[256],missing_count;
static unsigned observed_npc[256],observed_npc_count,missing_npc[256],missing_npc_count;
static uint16_t native_palettes[8][16],md_palettes[4][16];
static int native_ready;
static uint16_t cw_rhino_colors[16];
static uint16_t cw_hippo_colors[16];
static uint16_t cw_ride_colors[3][16];
static uint16_t graveyard_hyena_colors[16];
static uint16_t graveyard_bone_object_colors[16];
static uint16_t graveyard_pillar_colors[16];
static int graveyard_hyena_palette;
static unsigned next_scene;
void TlkMdSpritesNextScene(unsigned level) {next_scene=TlkNextSceneDataReady() && level>=3 && level<=13?level:0;}
void TlkMdSpritesGraveyardPalette(const uint16_t colors[64]) {
    graveyard_hyena_palette=colors!=NULL;
    if(colors)memcpy(graveyard_hyena_colors,colors+48,sizeof graveyard_hyena_colors);
    if(colors)memcpy(graveyard_bone_object_colors,colors+32,sizeof graveyard_bone_object_colors);
    if(colors)memcpy(graveyard_pillar_colors,colors+16,sizeof graveyard_pillar_colors);
}
static int graveyard_pillar_palette_matches(const uint16_t *colors) {
    static uint16_t previous[15];static int valid,matches;
    if(!valid || memcmp(previous,colors+1,sizeof previous)) {
        uint8_t bytes[30],hash[32];memcpy(previous,colors+1,sizeof previous);valid=1;
        for(unsigned i=0;i<15;i++){bytes[2*i]=(uint8_t)previous[i];bytes[2*i+1]=(uint8_t)(previous[i]>>8);}
        sha256_compute(bytes,sizeof bytes,hash);matches=!memcmp(hash,graveyard_pillar_palette_hash,32);
    }
    return matches;
}
static int graveyard_bone_object_palette_matches(const uint16_t *colors) {
    static uint16_t previous[15];static int valid,matches;
    if(!valid || memcmp(previous,colors+1,sizeof previous)) {
        uint8_t bytes[30],hash[32];memcpy(previous,colors+1,sizeof previous);valid=1;
        for(unsigned i=0;i<15;i++){bytes[2*i]=(uint8_t)previous[i];bytes[2*i+1]=(uint8_t)(previous[i]>>8);}
        sha256_compute(bytes,sizeof bytes,hash);
        matches=!memcmp(hash,graveyard_bone_object_palette_hash,32);
    }
    return matches;
}
void TlkMdSpritesCantWaitPalette(const uint16_t colors[64]) {
    if(colors)for(unsigned i=0;i<16;i++){
        cw_rhino_colors[i]=TlkMdColor555(colors[16+i]);
        cw_hippo_colors[i]=TlkMdColor555(colors[16+i]);
        for(unsigned bank=1;bank<=2;bank++)cw_ride_colors[bank][i]=TlkMdColor555(colors[bank*16+i]);
    }
}
static int cw_ride_palette_matches(unsigned bank,const uint16_t *colors) {
    if(bank<1 || bank>2)return 0;
    static uint16_t previous[2][15];static int valid[2],matches[2];unsigned n=bank-1;
    if(!valid[n] || memcmp(previous[n],colors+1,sizeof previous[n])) {
        uint8_t bytes[30],hash[32];memcpy(previous[n],colors+1,sizeof previous[n]);valid[n]=1;
        for(unsigned i=0;i<15;i++){bytes[i*2]=(uint8_t)previous[n][i];bytes[i*2+1]=(uint8_t)(previous[n][i]>>8);}
        sha256_compute(bytes,sizeof bytes,hash);
        matches[n]=!memcmp(hash,cw_ride_palette_hashes[n][0],32) || !memcmp(hash,cw_ride_palette_hashes[n][1],32);
    }
    return matches[n];
}
static int cw_rhino_palette_matches(const uint16_t *colors) {
    static uint16_t previous[15];static int valid,matches;
    if(!valid || memcmp(previous,colors+1,sizeof previous)) {
        uint8_t bytes[30],hash[32];memcpy(previous,colors+1,sizeof previous);valid=1;
        for(unsigned i=0;i<15;i++){bytes[i*2]=(uint8_t)previous[i];bytes[i*2+1]=(uint8_t)(previous[i]>>8);}
        sha256_compute(bytes,sizeof bytes,hash);
        matches=!memcmp(hash,cw_rhino_palette_hashes[0],32) || !memcmp(hash,cw_rhino_palette_hashes[1],32);
    }
    return matches;
}
static int cw_hippo_palette_matches(const uint16_t *colors) {
    static uint16_t previous[15];static int valid,matches;
    if(!valid || memcmp(previous,colors+1,sizeof previous)) {
        uint8_t bytes[30],hash[32];memcpy(previous,colors+1,sizeof previous);valid=1;
        for(unsigned i=0;i<15;i++){bytes[i*2]=(uint8_t)previous[i];bytes[i*2+1]=(uint8_t)(previous[i]>>8);}
        sha256_compute(bytes,sizeof bytes,hash);matches=!memcmp(hash,cw_hippo_palette_hash,32);
    }
    return matches;
}
static uint8_t *native_death_bank;
static size_t native_death_size;
static uint8_t *native_death_images[COUNT];
static uint8_t native_death_seen[COUNT];
static unsigned native_death_count;
static unsigned be16(const uint8_t *p) { return (unsigned)p[0]<<8|p[1]; }
static unsigned be32(const uint8_t *p) { return be16(p)<<16|be16(p+2); }
int TlkMdSpritesCubScene(unsigned level,unsigned descriptor) {
    return (level==0 && (descriptor==0x387 || descriptor==0x80d)) ||
           (level==1 && descriptor==0x3b9) || (level==2 && descriptor==0x3eb) ||
           (level==4 && descriptor==0x44f) || (level==5 && descriptor==0x481);
}
static int signed16(unsigned n) { return (int)(int16_t)n; }
static unsigned le16(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8; }
static void clear_native_death_images(void) {
    for(unsigned i=0;i<COUNT;i++) { free(native_death_images[i]);native_death_images[i]=NULL; }
    memset(native_death_seen,0,sizeof native_death_seen);native_death_count=0;
}
static void clear_native_death(void) {
    clear_native_death_images();free(native_death_bank);native_death_bank=NULL;native_death_size=0;
}
void TlkMdSpritesClear(void) {
    clear_native_death();
    memset(mixed_used,0,sizeof mixed_used);
    for (unsigned i=0;i<COUNT;i++) { free(images[i]);images[i]=NULL; }
    memset(seen,0,sizeof seen);missing_count=0;
    observed_npc_count=missing_npc_count=0;
    native_ready=0;graveyard_hyena_palette=0;
}
unsigned TlkMdSpritesCount(void) { return COUNT; }
unsigned TlkMdSpritesNativePose(unsigned external_pose) {
    unsigned found=0;
    for (unsigned i=0;i<COUNT;i++) if (sprite_map[i].md==external_pose && images[i] &&
        !(sprite_map[i].snes>=0x3e1000 && sprite_map[i].snes<=0x3e1007)) {
        unsigned pose=sprite_map[i].snes|0xc00000;
        if (found && found!=pose) return 0;
        found=pose;
    }
    return found;
}
static int piece_pixel(const uint8_t *rom,size_t size,unsigned at,int x,int y) {
    unsigned w=be16(rom+at),h=be16(rom+at+2),source=be32(rom+at+12);
    if (x<0 || y<0 || x>=(int)w || y>=(int)h) return 0;
    size_t p=source+((unsigned)x/8*(h/8)+(unsigned)y/8)*32+(unsigned)(y&7)*4+(unsigned)(x&7)/2;
    if (p>=size) return -1;
    return (rom[p]>>((x&1)?0:4))&15;
}
int TlkMdSpritesInit(const uint8_t *rom,size_t size) {
    TlkMdSpritesClear();if (!rom || size!=0x300000) return 0;
    unsigned palette=be32(rom+0x1cfdb4+44);
    if (palette>size-128) return 0;
    for (unsigned i=0;i<64;i++) md_palettes[i/16][i%16]=TlkMdColor555(be16(rom+palette+i*2));
    unsigned loaded=0;
    for (unsigned n=0;n<COUNT;n++) {
        const struct SpriteMap *m=&sprite_map[n];
        int pillar=TlkGraveyardPillarIndex(m->snes);
        if(pillar>=0 && m->role==TLK_MD_SPRITE_GRAVEYARD_PILLAR) {
            if(m->md!=0x922f4+(unsigned)pillar*8 || m->x!=-16 || m->y || m->w!=32 || m->h!=64)continue;
            unsigned first=be32(rom+m->md),tail=be32(rom+m->md+4);
            if(first!=0x9009c+(unsigned)pillar*512 || tail!=0x9109c+(unsigned)pillar*512 || tail>size-512)continue;
            uint8_t *image=calloc(32*64,1);if(!image)continue;
            for(unsigned y=0;y<64;y++)for(unsigned x=0;x<32;x++) {
                unsigned source=y<32?first:tail,sy=y&31;
                unsigned at=source+((sy/16)*8+(x/8)*2+(sy/8&1))*32+(sy&7)*4+(x&7)/2;
                image[y*32+x]=(uint8_t)((rom[at]>>((x&1)?0:4))&15);
            }
            images[n]=image;loaded++;continue;
        }
        if (m->md+24>size || m->w<=0 || m->h<=0 || m->w>256 || m->h>256) continue;
        unsigned count=be16(rom+m->md)+1;
        if (count>32 || m->md+24+count*16>size) continue;
        int minx=10000,miny=10000;int valid=1;
        for (unsigned i=0;i<count && valid;i++) {
            unsigned at=m->md+24+i*16,w=be16(rom+at),h=be16(rom+at+2);
            if (!w || !h || w>32 || h>32 || (w&7) || (h&7)) { valid=0;break; }
            int dx=signed16(be16(rom+at+4)),dy=signed16(be16(rom+at+6));
            for (unsigned y=0;y<h;y++) for (unsigned x=0;x<w;x++) {
                int c=piece_pixel(rom,size,at,(int)x,(int)y);
                if (c<0) { valid=0;break; }
                if (c) { if (dx+(int)x<minx) minx=dx+(int)x;if (dy+(int)y<miny) miny=dy+(int)y; }
            }
        }
        if (!valid || minx==10000) continue;
        uint8_t *image=(uint8_t*)calloc((size_t)m->w*m->h,1);if (!image) continue;
        for (unsigned remaining=count;remaining>0;remaining--) {
            unsigned i=remaining-1;
            unsigned at=m->md+24+i*16,w=be16(rom+at),h=be16(rom+at+2);
            int dx=signed16(be16(rom+at+4))-minx,dy=signed16(be16(rom+at+6))-miny;
            for (unsigned y=0;y<h;y++) for (unsigned x=0;x<w;x++) {
                int c=piece_pixel(rom,size,at,(int)x,(int)y),ix=dx+(int)x,iy=dy+(int)y;
                if (c && ix>=0 && iy>=0 && ix<m->w && iy<m->h) image[iy*m->w+ix]=(uint8_t)c;
            }
        }
        images[n]=image;loaded++;
    }
    return (int)loaded;
}
static unsigned find(unsigned pose);
static uint8_t *native_death_image(const uint8_t *rom,size_t size,unsigned index) {
    const struct SpriteMap *m=&sprite_map[index];unsigned p=m->snes;
    if(p>size-29 || m->w<=0 || m->h<=0 || m->w>256 || m->h>256)return NULL;
    unsigned flags=le16(rom+p),slots=flags&127,source=le16(rom+p+26);
    /* These explicit20 poses use the original bulk16x16 layout. Unsupported
     * formats never borrow the MD image as supposedly native artwork. */
    if((flags&0xff80)!=0x8000 || !slots || slots>32 || p+29+slots*4>size || rom[p+28]!=0x7f ||
       source>native_death_size || slots*128>native_death_size-source)return NULL;
    uint8_t *image=(uint8_t*)calloc((size_t)m->w*m->h,1);if(!image)return NULL;
    int minx=10000,miny=10000,maxx=-10000,maxy=-10000,valid=1;
    for(unsigned remaining=slots;remaining && valid;remaining--) {
        unsigned i=remaining-1,at=p+29+i*4;
        int dx=signed16(le16(rom+at)),dy=signed16(le16(rom+at+2));
        if(dx<-192 || dx>192 || dy<-192 || dy>192) { valid=0;break; }
        for(unsigned y=0;y<16 && valid;y++)for(unsigned x=0;x<16;x++) {
            unsigned address=source+i*64+(x>>3)*32+(y>>3)*slots*64+(y&7)*2,bit=7-(x&7),pixel=0;
            for(unsigned plane=0;plane<4;plane++)pixel|=((native_death_bank[address+(plane&1)+(plane>=2?16:0)]>>bit)&1u)<<plane;
            if(!pixel)continue;
            int px=dx+(int)x,py=dy+(int)y,ix=px-m->x,iy=py-m->y;
            if(ix<0 || iy<0 || ix>=m->w || iy>=m->h) { valid=0;break; }
            image[iy*m->w+ix]=(uint8_t)pixel;
            if(px<minx)minx=px;
            if(py<miny)miny=py;
            if(px>maxx)maxx=px;
            if(py>maxy)maxy=py;
        }
    }
    if(!valid || minx!=m->x || miny!=m->y || maxx+1!=m->x+m->w || maxy+1!=m->y+m->h ||
       !images[index] || memcmp(image,images[index],(size_t)m->w*m->h)) { free(image);return NULL; }
    return image;
}
void TlkMdSpritesBindSnes(const uint8_t *rom,size_t size) {
    clear_native_death();
    if (!rom || size!=0x300000) return;
    static const unsigned offsets[8]={0x7b93,0,0x2fac7,0,0x2fb07,0x2f727,0x7d53,0x2fb67};
    for (unsigned p=0;p<8;p++) if (offsets[p]) for (unsigned i=0;i<16;i++)
        native_palettes[p][i]=(uint16_t)(rom[offsets[p]+i*2] | rom[offsets[p]+i*2+1]<<8);
    native_ready=1;
    native_death_bank=(uint8_t*)malloc(65536);
    if(native_death_bank && (!TlkMdDecompress(rom,size,0x1fa78c,native_death_bank,65536,&native_death_size) ||
                            native_death_size!=17792)) {
        free(native_death_bank);native_death_bank=NULL;native_death_size=0;
    }
    if(!native_death_bank)return;
    for(unsigned i=0;i<sizeof cub_death_poses/sizeof cub_death_poses[0];i++) {
        unsigned n=find(cub_death_poses[i]);if(n==COUNT)break;
        native_death_images[n]=native_death_image(rom,size,n);if(!native_death_images[n])break;
        native_death_count++;
    }
    if(native_death_count!=sizeof cub_death_poses/sizeof cub_death_poses[0])clear_native_death_images();
}
int TlkMdSpritesCubDeathPose(unsigned pose) {
    pose&=0x3fffff;
    unsigned i=0;for(;i<sizeof cub_death_poses/sizeof cub_death_poses[0];i++)if(cub_death_poses[i]==pose)break;
    return i<sizeof cub_death_poses/sizeof cub_death_poses[0];
}
int TlkMdSpritesCubDeathReady(unsigned pose,const uint8_t *wram,size_t size) {
    return native_death_bank && wram && size==0x20000 && TlkMdSpritesCubDeathPose(pose) &&
           !memcmp(wram+0x10000,native_death_bank,native_death_size);
}
static unsigned find(unsigned pose) {
    pose&=0x3fffff;unsigned lo=0,hi=COUNT;
    while (lo<hi) { unsigned mid=(lo+hi)/2;if (sprite_map[mid].snes<pose) lo=mid+1;else hi=mid; }
    return lo<COUNT && sprite_map[lo].snes==pose && images[lo] ? lo : COUNT;
}
unsigned TlkMdSpritesCubDeathAssetCount(void) { return native_death_count; }
int TlkMdSpritesCubDeathPixel(unsigned pose,int x,int y,int md_frames) {
    if((md_frames!=0 && md_frames!=1) || !TlkMdSpritesCubDeathPose(pose))return -1;
    unsigned n=find(pose);if(n==COUNT || (!md_frames && !native_death_images[n]))return -1;
    const struct SpriteMap *m=&sprite_map[n];
    if(x<m->x || y<m->y || x>=m->x+m->w || y>=m->y+m->h)return 0;
    if(md_frames)return TlkMdSpritesPixel(pose,x,y);
    native_death_seen[n]=1;return native_death_images[n][(y-m->y)*m->w+x-m->x];
}
unsigned TlkMdSpritesRole(unsigned pose) { unsigned n=find(pose);return n<COUNT?sprite_map[n].role:0; }
/* The native coconut borrows Exile's rotating rock drawings, but original MD
 * Hakuna repeats only10EBC0. Keep that scene's existing constant body image. */
static unsigned npc_image_index(unsigned n) {
    unsigned pose=sprite_map[n].snes;
    if(next_scene==5 && sprite_map[n].role==TLK_MD_SPRITE_COCONUT &&
       (pose==0x60466 || pose==0x6048b || pose==0x604b0))return find(0xc60466);
    return n;
}
int TlkMdSpritesDescribe(unsigned pose,unsigned *md,unsigned *role,unsigned *native_palette,
                         unsigned *md_palette,unsigned *image_ready) {
    pose&=0x3fffff;unsigned lo=0,hi=COUNT;
    while(lo<hi){unsigned mid=(lo+hi)/2;if(sprite_map[mid].snes<pose)lo=mid+1;else hi=mid;}
    if(lo>=COUNT || sprite_map[lo].snes!=pose)return 0;
    unsigned image=npc_image_index(lo);
    if(md)*md=image<COUNT?sprite_map[image].md:0;
    if(role)*role=sprite_map[lo].role;
    if(native_palette)*native_palette=sprite_map[lo].native_palette;
    if(md_palette)*md_palette=sprite_map[lo].md_palette;
    if(image_ready)*image_ready=image<COUNT && images[image]!=NULL;
    return 1;
}
/* The same original rock drawings use bank2 in Exile and bank3 in Be Prepared. */
static int rolling_rock_pose(unsigned pose) {
    pose&=0x3fffff;
    return pose==0x603b5 || pose==0x603f0 || pose==0x6042b;
}
/* Source5094: these thirteen original stream operands share exact indexed
 * drawings. The live spider uses native bank5, original MD scene bank3.
 * Other users of shared poses retain their own captured-descriptor guards. */
static int hakuna_spider_pose(unsigned pose) {
    switch(pose&0x3fffff) {
    case 0x3b0fc:case 0x3b125:case 0x3b14e:case 0x3b17f:case 0x3b1b0:
    case 0x3b1d5:case 0x3b1fe:case 0x3b22b:case 0x3b258:
    case 0x3b289:case 0x3b2ae:case 0x3b2db:case 0x3b308:return 1;
    default:return 0;
    }
}
unsigned TlkMdSpritesDrawRole(unsigned pose,unsigned palette) {
    unsigned n=find(pose);
    if(n<COUNT && next_scene==5 && palette==5 && hakuna_spider_pose(pose))
        return TLK_MD_SPRITE_LATER_ENEMY;
    if(n<COUNT && next_scene==7 && palette==3 && rolling_rock_pose(pose) &&
       sprite_map[n].role==TLK_MD_SPRITE_LATER_WORLD && sprite_map[n].native_palette==2)
        return TLK_MD_SPRITE_LATER_WORLD;
    if(n<COUNT && next_scene==5 && sprite_map[n].role==TLK_MD_SPRITE_DEFEAT_PUFF &&
       sprite_map[n].native_palette==0 && palette==5)return TLK_MD_SPRITE_DEFEAT_PUFF;
    return n<COUNT && palette==sprite_map[n].native_palette ? sprite_map[n].role : 0;
}
void TlkMdSpritesObserveNpc(unsigned pose,unsigned palette) {
    if (palette!=2 && palette!=4 && palette!=6 && palette!=7 && !TlkMdSpritesRole(pose)) return;
    pose&=0x3fffff;
    unsigned n=0;for (;n<observed_npc_count;n++) if (observed_npc[n]==pose) return;
    if (n<256) observed_npc[observed_npc_count++]=pose;
    if (!TlkMdSpritesRole(pose) && missing_npc_count<256) missing_npc[missing_npc_count++]=pose;
}
int TlkMdSpritesBounds(unsigned pose,int *x,int *y,int *w,int *h) {
    unsigned n=find(pose);if (n==COUNT) return 0;
    *x=sprite_map[n].x;*y=sprite_map[n].y;*w=sprite_map[n].w;*h=sprite_map[n].h;return 1;
}
/* Optional, deduplicated evidence for visible source fallbacks. No pixel data
 * or game state is changed. Normal play does not open a trace file. */
static void npc_fallback_trace(unsigned pose,unsigned bank,unsigned role,const char *reason,
                               const uint16_t *actual,const uint16_t *expected) {
    TlkFallbackRecord("sampling_failure","graphics.sprites",reason,0,pose,(bank<<16)|role,1);
    static int initialized;static FILE *file;
    static struct {unsigned pose,bank,scene;uint16_t colors[15];} records[1024],last;
    static unsigned count;static int have_last;
    if(!initialized){initialized=1;const char *path=getenv("TLK_NPC_FALLBACK_TRACE");
        if(path)file=fopen(path,"w");
        if(file)fputs("pose,scene,bank,role,reason,actual,expected\n",file);
    }
    if(!file || !actual)return;
    if(have_last && last.pose==pose && last.bank==bank && last.scene==next_scene &&
       !memcmp(last.colors,actual+1,sizeof last.colors))return;
    last.pose=pose;last.bank=bank;last.scene=next_scene;memcpy(last.colors,actual+1,sizeof last.colors);have_last=1;
    for(unsigned i=0;i<count;i++)if(!memcmp(&records[i],&last,sizeof last))return;
    if(count<1024)records[count++]=last;else return;
    fprintf(file,"%06x,%u,%u,%u,%s,",pose,next_scene,bank,role,reason);
    for(unsigned i=1;i<16;i++)fprintf(file,"%04x",actual[i]);fputc(',',file);
    if(expected)for(unsigned i=1;i<16;i++)fprintf(file,"%04x",expected[i]);
    fputc('\n',file);fflush(file);
}
static int npc_sample(unsigned pose,int x,int y,unsigned native_pixel,int frames,int palette,
                          int native_bank,const uint16_t *cgram,uint16_t *color) {
    unsigned n=find(pose);if (n==COUNT || !sprite_map[n].role || !native_ready || !cgram || !color) {
        if(frames || palette)TlkFallbackRecord("sampling_failure","graphics.sprites",
            n==COUNT?"unmapped_pose":!native_ready?"native_palette_not_ready":"invalid_sample_context",0,pose,0,1);
        return -1;
    }
    const struct SpriteMap *m=&sprite_map[n];unsigned bank=m->native_palette;
    if(native_bank>=0) {
        int gorilla=next_scene==5 && m->role==TLK_MD_SPRITE_DEFEAT_PUFF && bank==0 && native_bank==5;
        int rock=next_scene==7 && m->role==TLK_MD_SPRITE_LATER_WORLD && bank==2 &&
                 native_bank==3 && rolling_rock_pose(pose);
        if(!gorilla && !rock){TlkFallbackRecord("sampling_failure","graphics.sprites","bank_owner_rejected",0,pose,(bank<<16)|(unsigned)native_bank,1);return -1;}
        bank=(unsigned)native_bank;
    }
    int prepared_geyser=next_scene==7 && m->role==TLK_MD_SPRITE_GRAVEYARD_PILLAR;
    int next=prepared_geyser || (next_scene>=3 && next_scene<=9 && m->role==TLK_MD_SPRITE_LATER_PICKUP && TlkWorldLifeSpritePose(pose)) ||
             (next_scene==3 && (m->role==TLK_MD_SPRITE_STAMPEDE_CUB || m->role==TLK_MD_SPRITE_STAMPEDE_ROCK)) ||
             (next_scene==4 && (m->role==TLK_MD_SPRITE_LIZARD || m->role==TLK_MD_SPRITE_PORCUPINE || m->role==TLK_MD_SPRITE_LEAVES || m->role==TLK_MD_SPRITE_PICKUP ||
                                (m->role==TLK_MD_SPRITE_LATER_WORLD && rolling_rock_pose(pose)))) ||
             (next_scene==5 && (m->role==TLK_MD_SPRITE_GORILLA || m->role==TLK_MD_SPRITE_PICKUP || m->role==TLK_MD_SPRITE_DEFEAT_PUFF)) ||
             ((next_scene==5 || next_scene==6) && m->role>=TLK_MD_SPRITE_LATER_ENEMY) ||
             (next_scene==6 && m->role==TLK_MD_SPRITE_PICKUP) ||
             ((next_scene==7 || next_scene==8 || next_scene==9) && (m->role==TLK_MD_SPRITE_ADULT_HYENA ||
                 m->role==TLK_MD_SPRITE_LATER_ENEMY || m->role==TLK_MD_SPRITE_LATER_WORLD ||
                 m->role==TLK_MD_SPRITE_LATER_PICKUP || m->role==TLK_MD_SPRITE_PICKUP || m->role==TLK_MD_SPRITE_SCAR)) ||
             (next_scene>=10 && next_scene<=13 && (m->role==TLK_MD_SPRITE_BONUS_TIMON ||
              m->role==TLK_MD_SPRITE_BONUS_PUMBAA || m->role==TLK_MD_SPRITE_PICKUP)) ||
             (next_scene==10 && ((m->role==TLK_MD_SPRITE_LATER_PICKUP && m->snes==0x50216) ||
              (m->role==TLK_MD_SPRITE_CONTINUE_TOKEN && m->snes==0x6f764)));
    const uint16_t *expected=next?TlkNextSceneNativeObj(next_scene,bank):native_palettes[bank];
    /* Preserve flashes and dynamically repurposed banks. */
    if(m->role==TLK_MD_SPRITE_GRAVEYARD_PILLAR && !prepared_geyser) {
        if(!graveyard_hyena_palette || !graveyard_pillar_palette_matches(cgram+128+bank*16)){
            npc_fallback_trace(pose,bank,m->role,"pillar_palette",cgram+128+bank*16,NULL);return -1;}
    } else if(m->role==TLK_MD_SPRITE_GRAVEYARD_BONE_OBJECT) {
        if(!graveyard_hyena_palette || !graveyard_bone_object_palette_matches(cgram+128+bank*16)){
            npc_fallback_trace(pose,bank,m->role,"bone_object_palette",cgram+128+bank*16,NULL);return -1;}
    } else if(m->role==TLK_MD_SPRITE_CW_RIDE_OBSTACLE && bank) {
        if(!cw_ride_palette_matches(bank,cgram+128+bank*16)){
            npc_fallback_trace(pose,bank,m->role,"ride_obstacle_palette",cgram+128+bank*16,NULL);return -1;}
    } else if(m->role==TLK_MD_SPRITE_CW_HIPPO) {
        if(!cw_hippo_palette_matches(cgram+128+bank*16)){
            npc_fallback_trace(pose,bank,m->role,"hippo_palette",cgram+128+bank*16,NULL);return -1;}
    } else if(m->role==TLK_MD_SPRITE_CW_RHINO || m->role==TLK_MD_SPRITE_CW_GIRAFFE) {
        if(!cw_rhino_palette_matches(cgram+128+bank*16)){
            npc_fallback_trace(pose,bank,m->role,m->role==TLK_MD_SPRITE_CW_GIRAFFE?"giraffe_palette":"rhino_palette",cgram+128+bank*16,expected);return -1;}
    } else if (!expected || memcmp(cgram+128+bank*16+1,expected+1,15*sizeof(uint16_t))) {
        npc_fallback_trace(pose,bank,m->role,"palette",cgram+128+bank*16,expected);return -1;}
    const uint16_t *external=(m->role==TLK_MD_SPRITE_CW_RHINO || m->role==TLK_MD_SPRITE_CW_GIRAFFE)?cw_rhino_colors:md_palettes[m->md_palette];
    if(m->role==TLK_MD_SPRITE_CW_HIPPO)external=cw_hippo_colors;
    if(m->role==TLK_MD_SPRITE_GRAVEYARD_BONE_OBJECT)external=graveyard_bone_object_colors;
    if(m->role==TLK_MD_SPRITE_GRAVEYARD_PILLAR)external=graveyard_pillar_colors;
    if(m->role==TLK_MD_SPRITE_CW_RIDE_OBSTACLE && bank)external=cw_ride_colors[bank];
    if(next)external=TlkNextSceneMdPalette(next_scene)+m->md_palette*16;
    int bonus_life=next_scene==10 && m->role==TLK_MD_SPRITE_LATER_PICKUP && m->snes==0x50216;
    if(bonus_life)external=TlkNextSceneMdPalette(next_scene)+3*16;
    const unsigned char *md_to_native=bonus_life?toss_life_md_to_native:m->md_to_native;
    const unsigned char *native_to_md=bonus_life?toss_life_native_to_md:m->native_to_md;
    if(prepared_geyser) {
        int phase=TlkGraveyardPillarIndex(pose);if(phase<0)return -1;
        md_to_native=prepared_geyser_md_to_native[phase];
        native_to_md=prepared_geyser_native_to_md[phase];
    }
    /* The original rain uses scene bank0, including the postfight fade.
     * Scenery and object palette choices remain independently selectable. */
    uint16_t weather_colors[64];
    if(next_scene==9 && m->snes==0x2f33e && TlkMdScenePaletteColors(9,weather_colors))external=weather_colors;
    if((m->role==TLK_MD_SPRITE_HYENA || m->role==TLK_MD_SPRITE_GRAVEYARD_VULTURE) && graveyard_hyena_palette)external=graveyard_hyena_colors;
    unsigned pixel=native_pixel&15;
    if (frames) {
        unsigned image=npc_image_index(n);
        if(image==COUNT)return -1;
        x-=m->x;y-=m->y;
        pixel=x<0 || y<0 || x>=m->w || y>=m->h ? 0 : images[image][y*m->w+x];seen[image]=1;
        if (!pixel) return 0;
        *color=palette ? external[pixel] : cgram[128+bank*16+md_to_native[pixel]];
    } else {
        if (!pixel) return 0;
        unsigned index=native_to_md[pixel];
        if(palette)index=TlkMixedPaletteIndex(index,cgram[128+bank*16+pixel],external,mixed_palette_used(n));
        *color=palette ? external[index] : cgram[128+bank*16+pixel];
    }
    return 1;
}
int TlkMdSpritesNpcSample(unsigned pose,int x,int y,unsigned native_pixel,int frames,int palette,
                          const uint16_t *cgram,uint16_t *color) {
    return npc_sample(pose,x,y,native_pixel,frames,palette,-1,cgram,color);
}
int TlkMdSpritesNpcSampleBank(unsigned pose,int x,int y,unsigned native_pixel,int frames,int palette,
                          unsigned native_bank,const uint16_t *cgram,uint16_t *color) {
    return npc_sample(pose,x,y,native_pixel,frames,palette,(int)native_bank,cgram,color);
}
int TlkMdSpritesHakunaSpiderSample(unsigned pose,int x,int y,unsigned native_pixel,int frames,int palette,
                                   const uint16_t *cgram,uint16_t *color) {
    unsigned n=find(pose);
    if(next_scene!=5 || !hakuna_spider_pose(pose) || n==COUNT || !native_ready || !cgram || !color)return -1;
    const uint16_t *expected=TlkNextSceneNativeObj(5,5),*external=TlkNextSceneMdPalette(5);
    if(!expected || !external || memcmp(cgram+128+5*16+1,expected+1,30)) {
        npc_fallback_trace(pose,5,TLK_MD_SPRITE_LATER_ENEMY,"spider_palette",cgram+128+5*16,expected);return -1;
    }
    unsigned pixel=native_pixel&15;
    if(frames) {
        const struct SpriteMap *m=&sprite_map[n];x-=m->x;y-=m->y;
        pixel=x<0 || y<0 || x>=m->w || y>=m->h?0:images[n][y*m->w+x];seen[n]=1;
    }
    if(!pixel)return 0;
    *color=palette?external[3*16+pixel]:cgram[128+5*16+pixel];
    return 1;
}
int TlkMdSpritesPixel(unsigned pose,int x,int y) {
    pose&=0x3fffff;
    unsigned lo=0,hi=COUNT;
    while (lo<hi) { unsigned mid=(lo+hi)/2;if (sprite_map[mid].snes<pose) lo=mid+1;else hi=mid; }
    if (lo==COUNT || sprite_map[lo].snes!=pose || !images[lo]) {
        TlkFallbackRecord("sampling_failure","graphics.sprites","missing_frame_image",0,pose,0,1);
        unsigned n=0;for (;n<missing_count;n++) if (missing[n]==pose) break;
        if (n==missing_count && n<256) missing[missing_count++]=pose;
        return -1;
    }
    seen[lo]=1;
    const struct SpriteMap *m=&sprite_map[lo];x-=m->x;y-=m->y;
    return x<0 || y<0 || x>=m->w || y>=m->h ? 0 : images[lo][y*m->w+x];
}
const TlkMdSpriteExtra *TlkMdSpritesExtras(unsigned pose,unsigned *count) {
    *count=0;pose&=0x3fffff;
    unsigned lo=0,hi=COUNT;
    while (lo<hi) { unsigned mid=(lo+hi)/2;if (sprite_map[mid].snes<pose) lo=mid+1;else hi=mid; }
    if (lo==COUNT || sprite_map[lo].snes!=pose || !images[lo]) return NULL;
    *count=sprite_map[lo].extra_count;return sprite_map[lo].extra;
}
void TlkMdSpritesReport(const char *path) {
    if (!path) return;
    FILE *f=fopen(path,"w");if (!f) return;
    unsigned count=0,roles[TLK_MD_SPRITE_ROLE_COUNT]={0};
    for (unsigned n=0;n<COUNT;n++) if (seen[n]) { count++;roles[sprite_map[n].role]++; }
    unsigned native_seen=0;for(unsigned n=0;n<COUNT;n++)native_seen+=native_death_seen[n]!=0;
    fprintf(f,"{\"later_roles\":{\"enemies\":%u,\"world\":%u,\"effects\":%u,\"pickups\":%u,\"destiny_monkeys\":%u},",
            roles[14],roles[15],roles[16],roles[17],roles[18]);
    fprintf(f,"\"owned_native_death_frames\":%u,\"seen_owned_native_death_frames\":%u,\"seen_owned_native_death_poses\":[",native_death_count,native_seen);
    unsigned native_emitted=0;for(unsigned n=0;n<COUNT;n++)if(native_death_seen[n])fprintf(f,"%s%u",native_emitted++?",":"",sprite_map[n].snes);
    fprintf(f,"],\"mapped_frames\":%u,\"seen_mapped_frames\":%u,\"missing_poses\":[",COUNT,count);
    for (unsigned n=0;n<missing_count;n++) fprintf(f,"%s%u",n?",":"",missing[n]);
    fprintf(f,"],\"observed_npc_poses\":%u,\"missing_npc_poses\":[",observed_npc_count);
    for (unsigned n=0;n<missing_npc_count;n++) fprintf(f,"%s%u",n?",":"",missing_npc[n]);
    fprintf(f,"],\"seen_by_role\":{\"cub\":%u,\"hyena\":%u,\"lizard\":%u,\"porcupine\":%u,\"pickup\":%u,\"leaves\":%u,\"defeat_puff\":%u,\"pickup_popup\":%u,\"continue_token\":%u,\"cw_rhino\":%u,\"graveyard_vulture\":%u,\"stampede_cub\":%u,\"stampede_rock\":%u,\"gorilla\":%u},\"seen_cub_poses\":[",
            roles[0],roles[1],roles[2],roles[3],roles[4],roles[5],roles[6],roles[7],roles[8],roles[9],roles[10],roles[11],roles[12],roles[13]);
    unsigned emitted=0;
    for (unsigned n=0;n<COUNT;n++) if (seen[n] && !sprite_map[n].role)
        fprintf(f,"%s{\"snes\":%u,\"md\":%u}",emitted++?",":"",sprite_map[n].snes,sprite_map[n].md);
    fprintf(f,"]}\n");fclose(f);
}
