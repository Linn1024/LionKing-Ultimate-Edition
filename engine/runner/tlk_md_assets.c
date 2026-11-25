#include "tlk_md_assets.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct MdScene {
    uint8_t *map, *tiles, *background, *blocks;
    size_t map_size, tile_size, bg_size, block_size;
    unsigned row_bytes, rows;
    uint16_t palette[64];
    uint16_t *native_blocks;
    unsigned native_count, matched;
    uint8_t *native_map;
    uint8_t *floor_profiles;
    uint8_t *md_markers,*native_markers;
    uint16_t *paired_blocks;
    size_t native_map_size;
    unsigned native_row_bytes, paired_matched;
    int valid;
} MdScene;
static MdScene scenes[14];
static struct { unsigned ready; uint16_t words[2048]; uint64_t native_mask[1024],md_mask[2048]; } native_layout[14];
static unsigned hakuna_phase;
/* Immutable initial/target tables are prepared in cache-v2. Live palette state
 * belongs to the saved view controller, never to the static asset package. */
static struct {
    uint16_t initial[2][64], target[100];
    int ready;
} cant_wait;
static uint16_t native_cache[128], mapped_native[2][128], mapped_external[2][64];
static int cache_level=-1, cache_mode=-1;
static unsigned be16(const uint8_t *p) { return (unsigned)p[0]*256+p[1]; }
static uint32_t be32(const uint8_t *p) { return (uint32_t)be16(p)<<16 | be16(p+2); }
uint16_t TlkMdColor555(unsigned c) {
    unsigned r=((c>>1)&7)*4+(((c>>1)&7)>>2);
    unsigned g=((c>>5)&7)*4+(((c>>5)&7)>>2);
    unsigned b=((c>>9)&7)*4+(((c>>9)&7)>>2);
    return (uint16_t)(r | g<<5 | b<<10);
}

int TlkMdDecompress(const uint8_t *rom, size_t size, size_t pos,
                    uint8_t *out, size_t cap, size_t *written) {
    size_t n=0, operations=0;
    if (written) *written=0;
    if (!rom || !out || !written || pos>=size) return 0;
    while (pos<size && ++operations<=cap+1) {
        unsigned command=rom[pos++];
        if (command==0x80) { *written=n; return 1; }
        size_t length, source;
        if (command<0x80) {
            if (pos>=size) return 0;
            length=(command>>4)+3;
            size_t distance=((command&15)<<8)|rom[pos++];
            if (!distance || distance>n) return 0;
            source=n-distance;
        } else if (command<0xc0) {
            length=command&63;
            if (length>cap-n || length>size-pos) return 0;
            memcpy(out+n,rom+pos,length); n+=length; pos+=length; continue;
        } else if (command==0xfe) {
            if (size-pos<3) return 0;
            length=rom[pos] | (unsigned)rom[pos+1]<<8;
            if (length>cap-n) return 0;
            memset(out+n,rom[pos+2],length); n+=length; pos+=3; continue;
        } else {
            if (command==0xff) {
                if (size-pos<4) return 0;
                length=rom[pos] | (unsigned)rom[pos+1]<<8; pos+=2;
            } else length=(command&63)+3;
            if (size-pos<2) return 0;
            source=rom[pos] | (unsigned)rom[pos+1]<<8; pos+=2;
            if (source>=n) return 0;
        }
        if (length>cap-n) return 0;
        for (size_t i=0;i<length;i++) out[n++]=out[source++];
    }
    return 0;
}
static uint8_t *decode(const uint8_t *rom, size_t size, uint32_t ptr, size_t *written) {
    uint8_t *p=(uint8_t*)malloc(65536);
    if (!p || !TlkMdDecompress(rom,size,ptr,p,65536,written)) { free(p); return NULL; }
    return p;
}
static unsigned scene_index(unsigned level) { return level==15 ? 4 : level; }
void TlkMdAssetsClear(void) {
    memset(native_layout,0,sizeof native_layout);
    hakuna_phase=0;
    memset(&cant_wait,0,sizeof cant_wait);
    for (unsigned i=0;i<14;i++) {
        free(scenes[i].map); free(scenes[i].tiles); free(scenes[i].background); free(scenes[i].blocks);
        free(scenes[i].native_blocks);
        free(scenes[i].native_map); free(scenes[i].paired_blocks);
        free(scenes[i].floor_profiles);
        free(scenes[i].md_markers);free(scenes[i].native_markers);
    }
    memset(scenes,0,sizeof scenes); cache_level=-1; cache_mode=-1;
}
int TlkMdAssetsInit(const uint8_t *rom, size_t size) {
    TlkMdAssetsClear();
    if (!rom || size!=0x300000) return 0;
    int ready=0;
    for (unsigned i=0;i<14;i++) {
        const uint8_t *record=rom+0x1cfdb4+i*48;
        MdScene *s=&scenes[i];
        s->row_bytes=be16(record+12); s->rows=be16(record+14);
        s->map=decode(rom,size,be32(record+16),&s->map_size);
        s->tiles=decode(rom,size,be32(record+28),&s->tile_size);
        s->background=decode(rom,size,be32(record+24),&s->bg_size);
        if (!s->map || !s->tiles || !s->background || !s->map_size || !s->tile_size || !s->bg_size || !s->row_bytes || (s->row_bytes&1) ||
            s->map_size!=(size_t)s->row_bytes*s->rows || s->bg_size%128) continue;
        if (i==5) {
            /* Original initializer08C400 starts Plane B with4096 raw bytes
             * at2218D6;18C0 streams rows from the full8192-byte source map.
             * Actor08C49A cycles four1440-byte waterfall uploads
             * from08C502 into tile byte28448; the generic LZ blob omits them.
             * Store all four images after the base bank during installation. */
            if(s->tile_size!=28448 || s->bg_size!=3584)continue;
            memcpy(s->background,rom+0x2218d6,8192);s->bg_size=8192;
            memcpy(s->tiles+s->tile_size,rom+0x8c502,4*1440);s->tile_size+=4*1440;
        }
        unsigned highest=0;
        for (size_t n=0;n+1<s->map_size;n+=2) {
            unsigned block=be16(s->map+n)&0xfff8;
            if (block>highest) highest=block;
        }
        uint32_t blocks=be32(record+20), palette=be32(record+44);
        /* This scene's descriptor names its live software palette in RAM.
         * Cache the verified initial table; the live view owns its fade. */
        if(i==1 && palette==0xffff845c)palette=0x1ea604;
        if (blocks>=size || (size_t)highest+8>size-blocks || palette>size-128) continue;
        s->block_size=highest+8;
        s->blocks=(uint8_t*)malloc(s->block_size);
        if (!s->blocks) continue;
        memcpy(s->blocks,rom+blocks,s->block_size);
        for (unsigned n=0;n<64;n++) {
            unsigned c=be16(rom+palette+n*2);
            /* Match the reference core's 3-bit -> 4-bit -> RGB565 response.
             * RGB555 presentation loses at most one green-channel bit. */
            s->palette[n]=TlkMdColor555(c);
        }
        if (i<=2 || i==6) {
            /* These reviewed worlds have matching contact heights at cells
             * with different decorative edges. Graveyard's 206 such cells
             * all match; two other height differences still require opacity
             * equality. Keep the per-cell test and changed-live-map guard. */
            uint32_t collision=be32(record+4),heights=be32(record+8);
            if (collision<size && (size_t)highest/2+4<=size-collision) {
                s->md_markers=(uint8_t*)malloc(s->map_size/2);
                if (s->md_markers) for (size_t n=0;n<s->map_size/2;n++)
                    s->md_markers[n]=rom[collision+(be16(s->map+n*2)&0xfff8)/2+3];
                /* Destiny needs marker homes only, not floor correspondence. */
                s->floor_profiles=i<=2 ? (uint8_t*)malloc(s->map_size/2*16) : NULL;
                if (s->floor_profiles) for (size_t n=0;n<s->map_size/2;n++) {
                    unsigned b=be16(s->map+n*2)&0xfff8;
                    unsigned offset=rom[collision+b/2]*16u;
                    if (heights>=size || offset+16>size-heights) {
                        free(s->floor_profiles);s->floor_profiles=NULL;break;
                    }
                    for (unsigned x=0;x<16;x++) s->floor_profiles[n*16+x]=rom[heights+offset+x]&31;
                }
            }
        }
        s->valid=1; ready++;
    }
    TlkMdCantWaitHydrate(rom,size);
    return ready;
}
int TlkMdCantWaitHydrate(const uint8_t *rom, size_t size) {
    memset(&cant_wait,0,sizeof cant_wait);
    const MdScene *s=&scenes[1];
    if (!rom || size!=0x300000 || be32(rom+0x1cfdb4+48+44)!=0xffff845c ||
        !s->background || !s->tiles || s->bg_size<28*128 || s->bg_size%128 || !s->tile_size) return 0;
    /* Reject incomplete tile hydration, rather than rendering missing cells. */
    for (size_t n=0;n<s->bg_size;n+=2)
        if (((size_t)(be16(s->background+n)&0x7ff)+1)*32>s->tile_size) return 0;
    for (unsigned variant=0;variant<2;variant++)
        for (unsigned i=0;i<64;i++)
            cant_wait.initial[variant][i]=(uint16_t)be16(rom+0x1ea604+variant*128+i*2);
    for (unsigned i=0;i<100;i++) cant_wait.target[i]=(uint16_t)be16(rom+0x1ea684+i*2);
    cant_wait.ready=1;
    return 1;
}
int TlkMdCantWaitReady(void) { return cant_wait.ready; }
int TlkMdCantWaitInitialPalette(unsigned variant,uint16_t colors[64]) {
    if (!cant_wait.ready || variant>1 || !colors) return 0;
    memcpy(colors,cant_wait.initial[variant],sizeof cant_wait.initial[variant]);return 1;
}
int TlkMdCantWaitPaletteStep(uint16_t colors[100]) {
    if (!cant_wait.ready || !colors) return 0;
    for (unsigned i=0;i<100;i++) {
        unsigned result=0;
        for (unsigned shift=1;shift<=9;shift+=4) {
            int value=(colors[i]>>shift)&7,goal=(cant_wait.target[i]>>shift)&7;
            value+=(goal>value)-(goal<value);result|=(unsigned)value<<shift;
        }
        colors[i]=(uint16_t)result;
    }
    return 1;
}
unsigned TlkMdCantWaitLineOffset(unsigned camera_x,unsigned wrap_x,unsigned y) {
    unsigned input=(camera_x+wrap_x)&65535;
    if (y>=224) return 0;
    if (y<152) return input/4;
    if (y<192) return input/2;
    return input/2+((input*(y-191))>>7);
}
uint16_t TlkMdCantWaitBackgroundPixel(unsigned camera_x,unsigned wrap_x,int x,int y) {
    if (!cant_wait.ready || y<0 || y>=224) return 0;
    const MdScene *s=&scenes[1];
    unsigned wx=((unsigned)x+TlkMdCantWaitLineOffset(camera_x,wrap_x,(unsigned)y))&511;
    unsigned tile=be16(s->background+(unsigned)(y/8)*128+(wx/8)*2);
    unsigned px=wx&7,py=(unsigned)y&7;
    if (tile&0x800) px=7-px;
    if (tile&0x1000) py=7-py;
    unsigned packed=s->tiles[(tile&0x7ff)*32+py*4+px/2];
    unsigned pixel=(packed>>((px&1)?0:4))&15;
    return pixel?(uint16_t)((tile&0x8000?11:7)<<12 | 0x900 | ((tile>>13)&3)*16 | pixel):0;
}
int TlkMdSceneReady(unsigned level) {
    level=scene_index(level); return level<14 && scenes[level].valid;
}
int TlkMdSceneBackgroundReady(unsigned level) {
    if(level==1)return TlkMdCantWaitReady();
    /* Hakuna needs the complete streamed source map and all waterfall images;
     * old generic scene data must never claim it is ready. */
    if(level==5 || level==7)return TlkMdSceneReady(5) && scenes[5].bg_size==8192 &&
        scenes[5].tile_size==28448+4*1440;
    return (level==0 || level==2 || level==4 || level==6 || level==7 || level==8 || level==9 || (level>=10 && level<=13)) && TlkMdSceneReady(level);
}
void TlkMdSceneAnimationPhase(unsigned level,unsigned phase) {
    if(level==5 || level==7)hakuna_phase=phase&3;
}
int TlkMdSceneSize(unsigned level, unsigned *width, unsigned *height) {
    level=scene_index(level);
    if (!width || !height || !TlkMdSceneReady(level)) return 0;
    *width=scenes[level].row_bytes/2*16; *height=scenes[level].rows*16; return 1;
}
static int wrap(int x, int size) { x%=size; return x<0 ? x+size : x; }
static int md_shape(const MdScene *s, unsigned block, uint8_t shape[256]) {
    if (block+8>s->block_size) return 0;
    for (unsigned y=0;y<16;y++) for (unsigned x=0;x<16;x++) {
        unsigned word=be16(s->blocks+block+(y/8*2+x/8)*2), px=x&7,py=y&7;
        if (word&0x800) px=7-px;
        if (word&0x1000) py=7-py;
        size_t at=(word&0x7ff)*32+py*4+px/2;
        if (at>=s->tile_size) return 0;
        shape[y*16+x]=(s->tiles[at]>>((px&1)?0:4))&15;
    }
    return 1;
}
static uint32_t shape_hash(const uint8_t *p) {
    uint32_t hash=2166136261u;
    for (unsigned i=0;i<256;i++) hash=(hash^p[i])*16777619u;
    return hash;
}
static unsigned le24(const uint8_t *p) { return p[0] | (unsigned)p[1]<<8 | (unsigned)p[2]<<16; }
int TlkMdAssetsBindSnes(const uint8_t *rom, size_t size) {
    if (!rom || size!=0x300000) return 0;
    int covered=0;
    for (unsigned level=0;level<14;level++) {
        MdScene *s=&scenes[level];
        free(s->native_blocks); s->native_blocks=NULL; s->native_count=s->matched=0;
        free(s->native_map); free(s->paired_blocks); s->native_map=NULL; s->paired_blocks=NULL;
        free(s->native_markers);s->native_markers=NULL;
        s->native_map_size=0; s->paired_matched=0;
        if (!s->valid) continue;
        unsigned rec=le24(rom+0x357+level*3)&0x3fffff;
        if (rec>size-0x32) continue;
        size_t gfx_size=0,map_size=0;
        uint8_t *gfx=decode(rom,size,le24(rom+rec+6)&0x3fffff,&gfx_size);
        uint8_t *map=decode(rom,size,le24(rom+rec+9)&0x3fffff,&map_size);
        unsigned blocks=le24(rom+rec+15)&0x3fffff, highest=0;
        if (!gfx || !map) { free(gfx); free(map); continue; }
        for (size_t i=0;i+1<map_size;i+=2) {
            unsigned b=(map[i] | (unsigned)map[i+1]<<8)&0xfff8;
            if (b>highest) highest=b;
        }
        if (blocks>=size || highest+8>size-blocks) { free(gfx); free(map); continue; }
        s->native_count=highest/8+1;
        s->native_blocks=(uint16_t*)malloc(s->native_count*sizeof(uint16_t));
        unsigned count=(unsigned)(s->block_size/8), capacity=16384;
        uint8_t *shapes=(uint8_t*)malloc((size_t)count*256);
        uint8_t *valid_md=(uint8_t*)calloc(count,1);
        uint8_t *valid_native=(uint8_t*)calloc(s->native_count,1);
        uint8_t *opacity=(uint8_t*)calloc(s->native_count,32);
        int *table=(int*)malloc(capacity*sizeof(int));
        if (!s->native_blocks || !shapes || !table || !valid_md || !opacity || !valid_native) {
            free(shapes); free(table); free(gfx); free(map); free(valid_md); free(valid_native); free(opacity);
            free(s->native_blocks); s->native_blocks=NULL; s->native_count=0; continue;
        }
        for (unsigned i=0;i<capacity;i++) table[i]=-1;
        for (unsigned i=0;i<count;i++) {
            uint8_t *shape=shapes+(size_t)i*256;
            if (!md_shape(s,i*8,shape)) continue;
            valid_md[i]=1;
            unsigned slot=shape_hash(shape)&(capacity-1);
            while (table[slot]>=0 && memcmp(shapes+(size_t)table[slot]*256,shape,256)) slot=(slot+1)&(capacity-1);
            if (table[slot]<0) table[slot]=(int)i;
        }
        for (unsigned i=0;i<s->native_count;i++) {
            uint8_t shape[256]; int valid=1;
            for (unsigned y=0;y<16;y++) for (unsigned x=0;x<16;x++) {
                const uint8_t *p=rom+blocks+i*8+(y/8*2+x/8)*2;
                unsigned word=p[0] | (unsigned)p[1]<<8, px=x&7,py=y&7;
                if (word&0x4000) px=7-px;
                if (word&0x8000) py=7-py;
                unsigned at=(word&1023)*32;
                if (at+32>gfx_size) { valid=0; shape[y*16+x]=0; continue; }
                unsigned value=0;
                for (unsigned plane=0;plane<4;plane++)
                    value|=((gfx[at+py*2+(plane&1)+(plane>=2?16:0)]>>(7-px))&1)<<plane;
                shape[y*16+x]=(uint8_t)value;
            }
            int match=-1;
            if (valid) {
                unsigned slot=shape_hash(shape)&(capacity-1);
                while (table[slot]>=0) {
                    if (!memcmp(shapes+(size_t)table[slot]*256,shape,256)) { match=table[slot]; break; }
                    slot=(slot+1)&(capacity-1);
                }
            }
            s->native_blocks[i]=match>=0 ? (uint16_t)(match*8) : 0xffff;
            valid_native[i]=(uint8_t)valid;
            if (match>=0) s->matched++;
            if (valid) for (unsigned pixel=0;pixel<256;pixel++)
                if (shape[pixel]) opacity[(size_t)i*32+pixel/8]|=(uint8_t)(1u<<(pixel&7));
        }
        s->native_map=map; s->native_map_size=map_size;
        s->native_row_bytes=rom[rec+18] | (unsigned)rom[rec+19]<<8;
        size_t collision_size=0;
        uint8_t *collision=(level<=2 || level==6) ? decode(rom,size,le24(rom+rec)&0x3fffff,&collision_size) : NULL;
        if (collision) {
            s->native_markers=(uint8_t*)malloc(map_size/2);
            if (s->native_markers) for (size_t n=0;n<map_size/2;n++) {
                unsigned offset=((map[n*2] | (unsigned)map[n*2+1]<<8)&0xfff8)/2;
                if (offset+4>collision_size) { free(s->native_markers);s->native_markers=NULL;break; }
                s->native_markers[n]=collision[offset+3];
            }
        }
        unsigned heights=le24(rom+rec+3)&0x3fffff;
        s->paired_blocks=(uint16_t*)malloc(map_size);
        if (s->paired_blocks) for (size_t n=0;n<map_size/2;n++) {
            unsigned native=(map[n*2] | (unsigned)map[n*2+1]<<8)&0xfff8;
            unsigned candidate=n*2+1<s->map_size ? be16(s->map+n*2)&0xfff8 : 0xffff;
            int same=valid_native[native/8] && s->native_row_bytes==s->row_bytes && candidate/8<count && valid_md[candidate/8];
            if (same) {
                int floor_equal=0;
                if (s->floor_profiles && collision && native/2+4<=collision_size && n<s->map_size/2) {
                    unsigned offset=collision[native/2] | (unsigned)collision[native/2+1]<<8;
                    floor_equal=heights<size && offset+16<=size-heights;
                    for (unsigned x=0;x<16 && floor_equal;x++)
                        if ((rom[heights+offset+x]&31)!=s->floor_profiles[n*16+x]) floor_equal=0;
                }
                const uint8_t *shape=shapes+(size_t)(candidate/8)*256;
                const uint8_t *mask=opacity+(size_t)(native/8)*32;
                for (unsigned pixel=0;pixel<256 && !floor_equal;pixel++)
                    if (!!shape[pixel] != !!(mask[pixel/8]&(1u<<(pixel&7)))) { same=0; break; }
            }
            s->paired_blocks[n]=same ? (uint16_t)candidate : 0xffff;
            if (same || s->native_blocks[native/8]!=0xffff) s->paired_matched++;
        }
        free(collision);
        free(shapes); free(table); free(gfx); free(valid_md); free(valid_native); free(opacity); covered++;
    }
    return covered;
}
int TlkMdSceneMarkerMove(unsigned level,unsigned marker,int native_x,int native_y,int *md_x,int *md_y) {
    if (level>9 || level==3 || !marker || !md_x || !md_y || native_x<0 || native_y<0 || (native_x&15) || (native_y&15)) return 0;
    const MdScene *s=&scenes[level];
    if (!s->md_markers || !s->native_markers || s->map_size!=s->native_map_size ||
        !s->row_bytes || s->row_bytes!=s->native_row_bytes) return 0;
    if ((unsigned)(native_y/16)>=s->map_size/s->row_bytes) return 0;
    unsigned columns=s->row_bytes/2,at=(unsigned)(native_y/16)*columns+(unsigned)(native_x/16);
    if ((unsigned)(native_x/16)>=columns || at>=s->map_size/2 || s->native_markers[at]!=marker) return 0;
    if (s->md_markers[at]==marker) return 0;
    unsigned native_count=0,md_count=0,target=0;
    for (unsigned n=0;n<s->map_size/2;n++) {
        native_count+=s->native_markers[n]==marker && s->md_markers[n]!=marker;
        if (s->md_markers[n]==marker && s->native_markers[n]!=marker) { md_count++;target=n; }
    }
    if (native_count!=1 || md_count!=1) return 0;
    *md_x=(int)(target%columns)*16;*md_y=(int)(target/columns)*16;return 1;
}
int TlkMdSceneMarkerDataReady(unsigned level) {
    if(level>=14)return 0;
    const MdScene *s=&scenes[level];
    return s->valid && s->md_markers && s->native_markers && s->row_bytes &&
        s->map_size==s->native_map_size && s->row_bytes==s->native_row_bytes;
}
int TlkMdSceneCoverage(unsigned level, unsigned *matched, unsigned *total) {
    level=scene_index(level);
    if (!matched || !total || level>=14 || !scenes[level].native_blocks) return 0;
    *matched=scenes[level].paired_blocks ? scenes[level].paired_matched : scenes[level].matched;
    *total=scenes[level].paired_blocks ? (unsigned)(scenes[level].native_map_size/2) : scenes[level].native_count;
    return 1;
}
/* The mixed preset keeps MD platforms and native materials. A block-level
 * correspondence cannot express a newly assembled shelf: match its 8x8 tiles
 * instead. Exact indexed matches win; version-specific details use the closest
 * original native material, strongly preserving the transparent silhouette.
 * The result never samples MD artwork or moves a gameplay object. */
static uint64_t MaterialMask(uint64_t m,unsigned flip) {
    if(flip&1){
        m=((m>>1)&UINT64_C(0x5555555555555555))|((m&UINT64_C(0x5555555555555555))<<1);
        m=((m>>2)&UINT64_C(0x3333333333333333))|((m&UINT64_C(0x3333333333333333))<<2);
        m=((m>>4)&UINT64_C(0x0f0f0f0f0f0f0f0f))|((m&UINT64_C(0x0f0f0f0f0f0f0f0f))<<4);
    }
    if(flip&2){
        m=((m>>8)&UINT64_C(0x00ff00ff00ff00ff))|((m&UINT64_C(0x00ff00ff00ff00ff))<<8);
        m=((m>>16)&UINT64_C(0x0000ffff0000ffff))|((m&UINT64_C(0x0000ffff0000ffff))<<16);
        m=(m>>32)|(m<<32);
    }
    return m;
}
int TlkMdSceneNativeLayoutTile(unsigned level,int x,int y,const uint8_t *rom,size_t size,uint16_t *word) {
    if((level!=5 && level!=6 && level!=7 && level!=8) || !word || !rom || size!=0x300000 ||
       !TlkMdSceneReady(level))return 0;
    const MdScene *s=&scenes[level];
    if(s->native_row_bytes!=s->row_bytes || s->native_map_size!=s->map_size)return 0;
    if(x<0 || y<0 || x>=(int)s->row_bytes*8 || y>=(int)s->rows*16)return 0;
    if(!native_layout[level].ready) {
        unsigned rec=le24(rom+0x357+level*3)&0x3fffff;
        if(rec>size-0x32)return 0;
        size_t gfx_size=0;
        uint8_t *gfx=decode(rom,size,le24(rom+rec+6)&0x3fffff,&gfx_size);
        if(!gfx || gfx_size>32768){free(gfx);return 0;}
        unsigned blocks=le24(rom+rec+15)&0x3fffff;
        uint16_t used[1024]={0},frequency[1024][8]={{0}};
        for(size_t i=0;i+1<s->native_map_size;i+=2) {
            unsigned cell=(s->native_map[i]|(unsigned)s->native_map[i+1]<<8)&0xfff8;
            if(blocks+cell+8>size)continue;
            for(unsigned q=0;q<4;q++) {
                unsigned t=rom[blocks+cell+q*2]|(unsigned)rom[blocks+cell+q*2+1]<<8;
                if((size_t)(t&1023)*32+32>gfx_size)continue;
                used[t&1023]=1;
                if(frequency[t&1023][t>>10&7]<65535)frequency[t&1023][t>>10&7]++;
            }
        }
        uint8_t shapes[1024][64];
        for(unsigned t=0;t<1024;t++)if(used[t])for(unsigned py=0;py<8;py++)for(unsigned px=0;px<8;px++) {
            unsigned at=t*32+py*2,v=0;
            for(unsigned p=0;p<4;p++)v|=((gfx[at+(p&1)+(p>=2?16:0)]>>(7-px))&1u)<<p;
            shapes[t][py*8+px]=(uint8_t)v;
            if((level==5 || level==7) && v)native_layout[level].native_mask[t]|=UINT64_C(1)<<(py*8+px);
        }
        free(gfx);
        for(unsigned mt=0;mt<2048;mt++) {
            native_layout[level].words[mt]=0xffff;
            if((size_t)mt*32+32>s->tile_size)continue;
            if(level==5 || level==7)for(unsigned py=0;py<8;py++)for(unsigned px=0;px<8;px++)
                if((s->tiles[mt*32+py*4+px/2]>>((px&1)?0:4))&15)
                    native_layout[level].md_mask[mt]|=UINT64_C(1)<<(py*8+px);
            unsigned best=~0u,best_word=0;
            for(unsigned nt=0;nt<1024;nt++)if(used[nt])for(unsigned flip=0;flip<4;flip++) {
                unsigned score=0;
                for(unsigned py=0;py<8 && score<best;py++)for(unsigned px=0;px<8 && score<best;px++) {
                    unsigned md=(s->tiles[mt*32+py*4+px/2]>>((px&1)?0:4))&15;
                    unsigned np=shapes[nt][(flip&2?7-py:py)*8+(flip&1?7-px:px)];
                    score+=(md!=np)+(!!md!=!!np)*64;
                }
                if(score<best) {
                    unsigned pal=0;
                    for(unsigned p=1;p<8;p++)if(frequency[nt][p]>frequency[nt][pal])pal=p;
                    best=score;best_word=nt|(pal<<10)|((flip&1)?0x4000:0)|((flip&2)?0x8000:0);
                }
                if(!best)break;
            }
            if(best!=~0u)native_layout[level].words[mt]=(uint16_t)best_word;
        }
        native_layout[level].ready=1;
    }
    size_t at=(size_t)(y/16)*s->row_bytes+(x/16)*2;
    unsigned block=(be16(s->map+at)&0xfff8)+((y&8)?4:0)+((x&8)?2:0);
    if(block+2>s->block_size)return 0;
    unsigned md=be16(s->blocks+block),native=native_layout[level].words[md&0x7ff];
    /* Native Hakuna trees and Be Prepared rocks fit most selected cells. Keep
     * their actual materials whenever opacity agrees; adapt changed ledges
     * instead of replacing an intact trunk with an unrelated closest tile. */
    if(level==5 || level==7){
        unsigned rec=le24(rom+0x357+level*3)&0x3fffff;
        unsigned table=le24(rom+rec+15)&0x3fffff;
        unsigned cell=(s->native_map[at]|(unsigned)s->native_map[at+1]<<8)&0xfff8;
        unsigned q=((y&8)?4:0)+((x&8)?2:0);
        if(table+cell+q+2<=size){
            unsigned original=rom[table+cell+q]|(unsigned)rom[table+cell+q+1]<<8;
            if(MaterialMask(native_layout[level].native_mask[original&1023],original>>14)==
               MaterialMask(native_layout[level].md_mask[md&0x7ff],md>>11&3)){
                *word=(uint16_t)((original&~0x2000u)|((md&0x8000)?0x2000:0));return 1;
            }
        }
    }
    if(native==0xffff)return 0;
    *word=(uint16_t)(native^((md&0x800)?0x4000:0)^((md&0x1000)?0x8000:0));
    if(md&0x8000)*word|=0x2000;
    return 1;
}
uint16_t TlkMdSceneMappedPixel(unsigned level, unsigned cell, unsigned x, unsigned y) {
    level=scene_index(level);
    if (!TlkMdSceneReady(level) || !scenes[level].native_blocks) return 0xffff;
    const MdScene *s=&scenes[level];
    unsigned id=(cell&0xfff8)/8;
    if (id>=s->native_count) return 0xffff;
    unsigned selected=s->native_blocks[id];
    size_t position=(size_t)(y/16)*s->native_row_bytes+(x/16)*2;
    if (s->paired_blocks && position+1<s->native_map_size && x<s->native_row_bytes*8 &&
        (s->native_map[position] | (unsigned)s->native_map[position+1]<<8)==cell && s->paired_blocks[position/2]!=0xffff)
        selected=s->paired_blocks[position/2];
    if (selected==0xffff) return 0xffff;
    x&=15; y&=15;
    unsigned block=selected+(y/8*2+x/8)*2;
    unsigned word=be16(s->blocks+block); x&=7; y&=7;
    if (word&0x800) x=7-x;
    if (word&0x1000) y=7-y;
    size_t at=(word&0x7ff)*32+y*4+x/2;
    if(level==5 && s->tile_size==28448+4*1440 && at>=28448 && at<28448+1440)
        at+=hakuna_phase*1440;
    if (at>=s->tile_size) return 0xffff;
    unsigned pixel=(s->tiles[at]>>((x&1)?0:4))&15;
    if (!pixel) return 0;
    return (uint16_t)((word&0x8000?12:8)<<12 | 0x800 | ((word>>13)&3)*16 | pixel);
}
uint16_t TlkMdScenePixel(unsigned level, unsigned layer, int wx, int wy, int cx, int cy,
                        int sx, int sy, int bgx, int bgy, int column, int width) {
    level=scene_index(level);
    if (!TlkMdSceneReady(level) || layer>1) return 0;
    const MdScene *s=&scenes[level];
    unsigned word; int px,py;
    if (!layer) {
        if (wx<0 || wy<0 || wx>=(int)s->row_bytes*8 || wy>=(int)s->rows*16) return 0;
        size_t cell=(size_t)(wy/16)*s->row_bytes+(unsigned)(wx/16)*2;
        unsigned block=(be16(s->map+cell)&0xfff8)+((wy&8)?4:0)+((wx&8)?2:0);
        if (block+2>s->block_size) return 0;
        word=be16(s->blocks+block); px=wx&7; py=wy&7;
    } else {
        /* Pride Lands' MD routine $08BA88 is verified against live VRAM.
         * Other scenes retain the selected SNES gameplay's raster scroll. */
        int x=bgx;
        if (level==0) {
            /* This panorama has distinct ends, not a seamless horizontal repeat.
             * Clamp the whole view, rather than wrapping negative margin pixels
             * to the distant right edge (or stretching individual edge pixels). */
            int view_left=cx-column;
            int origin=view_left>0 ? view_left*38/256 : 0;
            int last=width<512 ? 512-width : 0;
            if (origin<0) origin=0;
            if (origin>last) origin=last;
            x=origin+sx+column;
        }
        if (level==2) {
            /* Original 08BF34 / coefficient table 08C170. These are screen
             * bands, independent of the foreground's vertical camera. */
            unsigned shift=sy<96?5:sy<104?4:sy<128?3:sy<160?2:1;
            int origin=cx-column;
            /* Floor signed adaptation for an extended view left of world 0. */
            x=(origin>=0?origin/(1<<shift):-((-origin+(1<<shift)-1)/(1<<shift)))+sx+column;
        }
        if (level==4) {
            /* Original 08C1C8/08C26E: fixed first152 lines, then8/16/24/24
             * lines at1/16,1/8,1/4,1/2 camera X. Complete base tiles/names
             * match original live VRAM; vertical offset stays zero. */
            x=sx+column+(320-width)/2;
            if(sy>=152) {
                unsigned shift=sy<160?4:sy<176?3:sy<200?2:1;
                int origin=cx-column;
                x=(origin>=0?origin/(1<<shift):-((-origin+(1<<shift)-1)/(1<<shift)))+sx+column;
            }
        }
        if(level==7) {
            /* Original08E77C/08E7A4: uniform half camera X, fixed Y=0.
             * Initializer disables the preceding scene's line-table DMA;
             * old C610 row words are stale, not this scene's scroll recipe.
             * Complete names, used tiles and all64 colors match live VDP. */
            int origin=cx-column;
            x=(origin>=0?origin/2:-((-origin+1)/2))+sx+column;
        }
        if(level==8) {
            /* Original08E7E8/08EA00:112/39/73 screen lines at1/8,1/4,1/2
             * camera X, fixed Y. All224 actual completed VDP rows match;
             * do not round the authored middle band to40 lines. */
            unsigned shift=sy<112?3:sy<151?2:1;int origin=cx-column;
            x=(origin>=0?origin/(1<<shift):-((-origin+(1<<shift)-1)/(1<<shift)))+sx+column;
        }
        if(level==9) {
            /* Original08E2B0/08E532:96/88/40 lines,1/2,1/4,1/2 X,Y=0. */
            unsigned shift=sy<96?1:sy<184?2:1;int origin=cx-column;
            x=(origin>=0?origin/(1<<shift):-((-origin+(1<<shift)-1)/(1<<shift)))+sx+column;
        }
        if(level>=10 && level<=13) {
            /* Original08C252, common08E738 after Hunt's30-update init delay:
             * fixed plane offsets0, complete static names and used tiles. */
            x=sx+column+(320-width)/2;
        }
        int y=level==0 ? cy*20/256+sy : (level==2 || level==4 || level==6 || level==7 || level==8 || level==9 || (level>=10 && level<=13)) ? sy : level==5 ? cy*5/16+sy : bgy;
        if(level==5 || level==6) {
            /* Hakuna08DB82 writes a512-line table backwards: first8 fixed,
             * then136/96/272 at1/8,1/4,1/2. Vertical camera selects the table
             * window as well as Plane B's Y. Destiny08DFDA instead has five
             * screen bands96/16/32/48/32, Y=0. Neither uses native BG scroll. */
            int origin=cx-column,shift;
            if(level==5 || level==7)shift=y<8?0:y<144?3:y<240?2:1;
            else shift=sy<96?5:sy<112?4:sy<144?3:sy<192?2:1;
            int offset=level==5 && y<8?0:
                origin>=0?origin/(1<<shift):-((-origin+(1<<shift)-1)/(1<<shift));
            x=offset+sx+column;
        }
        x=wrap(x,512); y=wrap(y,(int)(s->bg_size/128)*8);
        word=be16(s->background+(size_t)(y/8)*128+(unsigned)(x/8)*2); px=x&7; py=y&7;
    }
    if (word&0x800) px=7-px;
    if (word&0x1000) py=7-py;
    size_t at=(word&0x7ff)*32+(unsigned)py*4+(unsigned)px/2;
    if(level==5 && s->tile_size==28448+4*1440 && at>=28448 && at<28448+1440)
        at+=hakuna_phase*1440;
    if (at>=s->tile_size) return 0;
    unsigned pixel=(s->tiles[at]>>((px&1)?0:4))&15;
    if (!pixel) return 0;
    unsigned priority=word&0x8000 ? (layer?11:12) : (layer?7:8);
    return (uint16_t)(priority<<12 | 0x800 | layer<<8 | ((word>>13)&3)*16 | pixel);
}
uint16_t TlkMdSceneBackgroundViewPixel(unsigned level,int view_left,int camera_y,int x,int y,int width) {
    if (!TlkMdSceneBackgroundReady(level)) return 0;
    return TlkMdScenePixel(level,1,0,0,view_left,camera_y,x,y,0,0,0,width);
}
static unsigned difference(unsigned a,unsigned b) {
    int r=(int)(a&31)-(int)(b&31), g=(int)((a>>5)&31)-(int)((b>>5)&31), z=(int)((a>>10)&31)-(int)((b>>10)&31);
    return (unsigned)(r*r*3+g*g*6+z*z*2);
}
void TlkMdScenePalette(unsigned level, const uint16_t *cgram, int md_palette) {
    level=scene_index(level);
    if (!TlkMdSceneReady(level) || !cgram) { cache_level=-1; return; }
    cache_mode=!!md_palette;
    if (cache_level==(int)level && !memcmp(native_cache,cgram,sizeof native_cache)) return;
    const MdScene *s=&scenes[level];
    memcpy(native_cache,cgram,sizeof native_cache); cache_level=(int)level; cache_mode=md_palette;
    for (unsigned i=0;i<128;i++) {
        unsigned best=~0u, index=16;
        for (unsigned j=16;j<64;j++) {
            unsigned d=difference(cgram[i],s->palette[j]);
            if (d<best) { best=d; index=j; }
        }
        mapped_native[0][i]=cgram[i];mapped_native[1][i]=s->palette[index];
        /* Bonus jungle/wood palettes1/2 share indexed meanings. RGB-nearest
         * wrongly maps their dark blues to teal and creates tile boundaries. */
        if(level>=10 && level<=13 && i>=16 && i<48)mapped_native[1][i]=s->palette[i];
    }
    for (unsigned i=0;i<64;i++) {
        unsigned best=~0u, index=0;
        for (unsigned j=0;j<128;j++) {
            unsigned d=difference(s->palette[i],cgram[j]);
            if (d<best) { best=d; index=j; }
        }
        mapped_external[0][i]=cgram[index];mapped_external[1][i]=s->palette[i];
        if(level>=10 && level<=13 && i>=16 && i<48)mapped_external[0][i]=cgram[i];
    }
}
int TlkMdScenePaletteColors(unsigned level, uint16_t colors[64]) {
    level=scene_index(level);
    if (!colors || !TlkMdSceneReady(level)) return 0;
    memcpy(colors,scenes[level].palette,sizeof scenes[level].palette);
    return 1;
}
uint16_t TlkMdSceneColor(unsigned index, int external, uint16_t original) {
    if (cache_level<0) return original;
    if (external) return index<64 ? mapped_external[!!cache_mode][index] : original;
    return index<128 ? mapped_native[!!cache_mode][index] : original;
}
uint16_t TlkMdSceneModeColor(unsigned index,int external,uint16_t original,int md) {
    if(cache_level<0)return original;
    return external?(index<64?mapped_external[!!md][index]:original):(index<128?mapped_native[!!md][index]:original);
}
#include "tlk_md_assets_cache.inc"

void TlkMdScenePreparedPalette(unsigned level,const uint16_t colors[64]) {
    if(level!=9 || !colors || !TlkMdSceneReady(level))return;
    if(memcmp(scenes[level].palette,colors,sizeof scenes[level].palette)) {
        memcpy(scenes[level].palette,colors,sizeof scenes[level].palette);cache_level=-1;
    }
}

/* Resolve names once per tile row; scalar sampling remains the fallback. */
static int MdSceneTileRow(unsigned level,const MdScene *s,unsigned word,unsigned layer,unsigned x,unsigned y,uint16_t *out,unsigned count){
 if(!out || !count || count>8-(x&7))return 0;
 unsigned py=y&7;if(word&0x1000)py=7-py;
 size_t at=(word&0x7ff)*32+py*4;
 if(level==5 && s->tile_size==28448+4*1440 && at>=28448 && at<28448+1440)at+=hakuna_phase*1440;
 if(at+3>=s->tile_size)return 0;
 unsigned token=((word&0x8000?(layer?11:12):(layer?7:8))<<12)|0x800|(layer<<8)|((word>>13&3)<<4);
 for(unsigned j=0;j<count;j++){unsigned px=(x+j)&7;if(word&0x800)px=7-px;
  unsigned pixel=s->tiles[at+px/2]>>((px&1)?0:4)&15;out[j]=pixel?(uint16_t)(token|pixel):0;}
 return 1;
}
int TlkMdSceneMappedPixels(unsigned level,unsigned cell,unsigned x,unsigned y,uint16_t *out,unsigned count){
 level=scene_index(level);if(!TlkMdSceneReady(level)||!scenes[level].native_blocks)return 0;const MdScene *s=&scenes[level];
 unsigned id=(cell&0xfff8)/8;if(id>=s->native_count)return 0;unsigned selected=s->native_blocks[id];
 size_t position=(size_t)(y/16)*s->native_row_bytes+(x/16)*2;
 if(s->paired_blocks && position+1<s->native_map_size && x<s->native_row_bytes*8 &&
  (s->native_map[position]|(unsigned)s->native_map[position+1]<<8)==cell && s->paired_blocks[position/2]!=0xffff)selected=s->paired_blocks[position/2];
 if(selected==0xffff)return 0;unsigned block=selected+(((y&15)/8)*2+(x&15)/8)*2;
 if(block+2>s->block_size)return 0;return MdSceneTileRow(level,s,be16(s->blocks+block),0,x,y,out,count);
}
int TlkMdSceneForegroundPixels(unsigned level,int x,int y,uint16_t *out,unsigned count){
 level=scene_index(level);if(!TlkMdSceneReady(level))return 0;const MdScene *s=&scenes[level];
 if(x<0||y<0||x>=(int)s->row_bytes*8||y>=(int)s->rows*16)return 0;
 size_t cell=(size_t)(y/16)*s->row_bytes+(unsigned)(x/16)*2;unsigned block=(be16(s->map+cell)&0xfff8)+((y&8)?4:0)+((x&8)?2:0);
 if(block+2>s->block_size)return 0;return MdSceneTileRow(level,s,be16(s->blocks+block),0,(unsigned)x,(unsigned)y,out,count);
}
int TlkMdSceneBackgroundPixels(unsigned level,int x,int y,uint16_t *out,unsigned count){
 level=scene_index(level);if(!TlkMdSceneBackgroundReady(level))return 0;const MdScene *s=&scenes[level];
 x=wrap(x,512);y=wrap(y,(int)(s->bg_size/128)*8);unsigned word=be16(s->background+(size_t)(y/8)*128+(unsigned)(x/8)*2);
 return MdSceneTileRow(level,s,word,1,(unsigned)x,(unsigned)y,out,count);
}
